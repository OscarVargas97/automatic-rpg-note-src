from django.core.management.base import BaseCommand
from faster_whisper import WhisperModel

MODEL_SIZE = "small"


class Command(BaseCommand):
    help = (
        "Deja listo el modelo de Whisper local para transcribir: descarga el modelo "
        f"'{MODEL_SIZE}' si hace falta y confirma si va a correr en GPU o CPU."
    )

    def handle(self, *args, **options):
        try:
            WhisperModel(MODEL_SIZE, device="cuda", compute_type="float16")
            device = "GPU (cuda, float16)"
        except Exception:
            WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
            device = "CPU (int8)"

        self.stdout.write(
            self.style.SUCCESS(f"Modelo '{MODEL_SIZE}' listo para transcribir — {device}.")
        )
