from django.core.management.base import BaseCommand

from core.transcription import MODEL_SIZE, load_model


class Command(BaseCommand):
    help = (
        "Deja listo el modelo de Whisper local para transcribir: descarga el modelo "
        f"'{MODEL_SIZE}' si hace falta y confirma si va a correr en GPU o CPU."
    )

    def handle(self, *args, **options):
        _model, device = load_model()

        self.stdout.write(
            self.style.SUCCESS(f"Modelo '{MODEL_SIZE}' listo para transcribir — {device}.")
        )
