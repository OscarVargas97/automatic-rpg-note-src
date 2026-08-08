import av
import numpy as np
from faster_whisper import WhisperModel

MODEL_SIZE = "small"


def get_audio_duration(path: str) -> float:
    """Duration in seconds, read from container metadata — avoids decoding the whole file
    just to know its length (used for transcription progress)."""
    with av.open(path, mode="r", metadata_errors="ignore") as container:
        if container.duration is not None:
            return container.duration / av.time_base
        stream = container.streams.audio[0]
        return float(stream.duration * stream.time_base)


def _validate_inference(model: WhisperModel) -> None:
    """Forces a minimal transcription before trusting the model.

    Constructing WhisperModel(device="cuda") doesn't always fail if compute libraries are
    missing (e.g. cuBLAS) — CTranslate2 only loads them on first real use, not when the
    object is built. Without this check, load_model() could report "GPU" and only fail
    during an actual transcription.
    """
    silence = np.zeros(16000, dtype=np.float32)  # 1s of silence at 16kHz
    segments, _info = model.transcribe(silence)
    list(segments)  # faster-whisper's generator does nothing until consumed


def load_model() -> tuple[WhisperModel, str]:
    """Loads the local Whisper model. GPU (cuda/float16) if available, otherwise CPU (int8)."""
    try:
        model = WhisperModel(MODEL_SIZE, device="cuda", compute_type="float16")
        _validate_inference(model)
        return model, "GPU (cuda, float16)"
    except Exception:
        return WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8"), "CPU (int8)"
