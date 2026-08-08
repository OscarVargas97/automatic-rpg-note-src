from pathlib import Path

import numpy as np
import torch
from sklearn.cluster import AgglomerativeClustering

from django.conf import settings

# How much audio each embedding is computed over — long enough for ECAPA-TDNN to produce a
# stable speaker embedding, short enough to still localize a speaker change within a segment.
WINDOW_SECONDS = 1.5
SAMPLE_RATE = 16000


def load_diarization_models():
    """Loads Silero VAD and SpeechBrain's ECAPA-TDNN speaker embedding model — both public,
    no HuggingFace account or token needed (verified in Tema #5)."""
    from silero_vad import load_silero_vad
    from speechbrain.inference.speaker import EncoderClassifier

    vad_model = load_silero_vad()
    embedding_model = EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        savedir=str(Path(settings.DIARIZATION_MODELS_DIR) / "spkrec-ecapa-voxceleb"),
    )
    return vad_model, embedding_model


def diarize(
    audio_path: str, num_speakers: int, vad_model, embedding_model
) -> list[tuple[float, float, str]]:
    """Returns (start, end, speaker_label) windows for audio_path, clustering speaker
    embeddings into num_speakers groups. Empty list if no speech is detected — callers fall
    back to unlabeled transcription in that case."""
    from faster_whisper.audio import decode_audio
    from silero_vad import get_speech_timestamps

    # silero_vad.read_audio() goes through torchaudio, which on this stack (torchaudio
    # 2.9+) requires the separate `torchcodec` package and breaks without it — decode with
    # PyAV instead (same decoder faster-whisper already uses, no extra dependency).
    wav = torch.from_numpy(decode_audio(audio_path, sampling_rate=SAMPLE_RATE))
    speech_timestamps = get_speech_timestamps(wav, vad_model, return_seconds=True)
    if not speech_timestamps:
        return []

    windows: list[tuple[float, float]] = []
    for ts in speech_timestamps:
        cur = ts["start"]
        while cur < ts["end"]:
            windows.append((cur, min(cur + WINDOW_SECONDS, ts["end"])))
            cur += WINDOW_SECONDS
    windows = [(start, end) for start, end in windows if end - start >= 0.5]
    if not windows:
        return []

    embeddings = []
    for start, end in windows:
        chunk = wav[int(start * SAMPLE_RATE) : int(end * SAMPLE_RATE)]
        with torch.no_grad():
            embedding = embedding_model.encode_batch(chunk.unsqueeze(0))
        embeddings.append(embedding.squeeze().cpu().numpy())

    n_clusters = min(num_speakers, len(windows))
    labels = AgglomerativeClustering(n_clusters=n_clusters).fit_predict(np.stack(embeddings))

    return [
        (start, end, f"SPEAKER_{label:02d}")
        for (start, end), label in zip(windows, labels)
    ]


def label_for(windows: list[tuple[float, float, str]], start: float, end: float) -> str | None:
    """Speaker label of the diarization window that overlaps [start, end] the most, or None
    if windows is empty or nothing overlaps."""
    best_label = None
    best_overlap = 0.0
    for w_start, w_end, label in windows:
        overlap = min(end, w_end) - max(start, w_start)
        if overlap > best_overlap:
            best_overlap = overlap
            best_label = label
    return best_label
