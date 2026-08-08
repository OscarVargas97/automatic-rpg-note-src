from datetime import datetime, timezone
from pathlib import Path

from huey.contrib.djhuey import db_task

from core.transcription import get_audio_duration, load_model

from .models import TranscriptionJob


@db_task()
def transcribe_job(job_id: int) -> None:
    """Transcribes a TranscriptionJob's audios and writes the raw into the project's raws/.

    Each audio is transcribed separately (faster-whisper decodes whatever format it is) and
    the resulting segments are merged with a cumulative time offset — raw audio is never
    concatenated, see decision log 2026-08-07 in docs/meta/contexto-para-ia.md.
    """
    job = TranscriptionJob.objects.select_related("project").get(pk=job_id)
    job.status = TranscriptionJob.IN_PROGRESS
    job.progress = 0.0
    job.save(update_fields=["status", "progress", "updated_at"])

    try:
        model, _device = load_model()
        audios = list(job.audios.all())
        total_duration = sum(get_audio_duration(a.file.path) for a in audios)

        # Diarization is opt-in per job (speaker_count set at upload) — importing
        # core.diarization pulls in PyTorch/SpeechBrain, so it stays out of the process for
        # jobs that don't ask for it.
        diarize = label_for = None
        vad_model = embedding_model = None
        if job.speaker_count:
            from core.diarization import diarize, label_for, load_diarization_models

            vad_model, embedding_model = load_diarization_models()

        lines: list[str] = []
        offset = 0.0
        last_saved_pct = -1

        for audio in audios:
            diarization_windows: list[tuple[float, float, str]] = []
            if job.speaker_count:
                diarization_windows = diarize(
                    audio.file.path, job.speaker_count, vad_model, embedding_model
                )

            segments, _info = model.transcribe(audio.file.path)
            lines.append(f"## {audio.file.name}")
            audio_end = offset
            for seg in segments:
                start = offset + seg.start
                end = offset + seg.end
                audio_end = max(audio_end, end)

                prefix = ""
                if diarization_windows:
                    speaker = label_for(diarization_windows, seg.start, seg.end)
                    if speaker:
                        prefix = f"{speaker}: "

                lines.append(f"[{start:.2f} - {end:.2f}] {prefix}{seg.text.strip()}")

                # Segments arrive every few seconds of audio — cheap enough to persist
                # progress on each one, throttled to one write per whole percentage point.
                if total_duration > 0:
                    pct = min(100.0, end / total_duration * 100)
                    if int(pct) != last_saved_pct:
                        last_saved_pct = int(pct)
                        job.progress = pct
                        job.save(update_fields=["progress", "updated_at"])
            offset = audio_end

        raws_dir = Path(job.project.vault_path) / "raws"
        raws_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{datetime.now(timezone.utc):%Y-%m-%d_%H%M%S}_job-{job.pk}.md"
        raw_path = raws_dir / filename
        raw_path.write_text("\n".join(lines), encoding="utf-8")

        job.raw_path = str(raw_path)
        job.status = TranscriptionJob.DONE
        job.progress = 100.0
        job.save(update_fields=["raw_path", "status", "progress", "updated_at"])

        # Extension point: this is where Claude ingestion would hook in (Pipeline de
        # ingesta y enrutamiento.md) once that piece exists — today the pipeline ends at
        # the raw file.
    except Exception as exc:
        job.status = TranscriptionJob.ERROR
        job.error_message = str(exc)
        job.save(update_fields=["status", "error_message", "updated_at"])
