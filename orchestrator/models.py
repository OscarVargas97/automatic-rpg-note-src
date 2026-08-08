import re
from pathlib import Path

from django.db import models

# Literal folder names of the campaign vault schema — defined by
# docs/diseno-del-sistema/Esquema del vault de campaña.md, not free to translate: this is
# what the user actually sees in their Obsidian vault.
CAMPAIGN_FOLDERS = [
    "personajes",
    "lugares",
    "facciones",
    "objetos",
    "hilos-narrativos",
    "partidas",
]

_WINDOWS_DRIVE_PATH = re.compile(r"^([A-Za-z]):[\\/]")


def normalize_windows_path(path: str) -> str:
    """Translates a pasted Windows-style path (C:\\Users\\... or C:/Users/...) to its WSL
    mount equivalent (/mnt/c/Users/...). Server runs under WSL, where Windows drives are
    reachable but only under /mnt/<drive letter>, not their native C:\\ form. Paths that
    aren't Windows-style are returned unchanged."""
    match = _WINDOWS_DRIVE_PATH.match(path)
    if not match:
        return path
    drive = match.group(1).lower()
    rest = path[match.end():].replace("\\", "/")
    return f"/mnt/{drive}/{rest}"


def vault_exists(vault_path: str) -> bool:
    """True if vault_path already has the minimum campaign vault structure."""
    base = Path(vault_path)
    return (base / "raws").is_dir() and (base / "campaña").is_dir()


def ensure_vault_structure(vault_path: str) -> None:
    """Creates raws/ and campaña/{...}/ under vault_path if missing. Never touches existing files."""
    base = Path(vault_path)
    base.mkdir(parents=True, exist_ok=True)
    (base / "raws").mkdir(exist_ok=True)
    for folder in CAMPAIGN_FOLDERS:
        (base / "campaña" / folder).mkdir(parents=True, exist_ok=True)


class CampaignProject(models.Model):
    """A campaign/vault destination — not to be confused with the Django project itself."""

    name = models.CharField(max_length=200)
    vault_path = models.CharField(
        max_length=1000,
        help_text="Filesystem path to this campaign's Obsidian vault.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        # A relative vault_path would resolve against the server process's cwd instead of
        # a real vault location — reject it before ensure_vault_structure() can act on it.
        if not Path(self.vault_path).is_absolute():
            raise ValueError(f"vault_path debe ser una ruta absoluta: {self.vault_path!r}")
        super().save(*args, **kwargs)
        ensure_vault_structure(self.vault_path)


class TranscriptionJob(models.Model):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ERROR = "error"
    STATUS_CHOICES = [
        (PENDING, "Pendiente"),
        (IN_PROGRESS, "En curso"),
        (DONE, "Listo"),
        (ERROR, "Error"),
    ]

    project = models.ForeignKey(
        CampaignProject, on_delete=models.CASCADE, related_name="jobs"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    progress = models.FloatField(
        default=0.0, help_text="Percent (0-100) of total audio duration transcribed so far."
    )
    speaker_count = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Number of distinct speakers to diarize into. Empty means no diarization.",
    )
    raw_path = models.CharField(max_length=1000, blank=True, default="")
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Job #{self.pk} — {self.project.name} ({self.status})"


class UploadedAudio(models.Model):
    job = models.ForeignKey(
        TranscriptionJob, on_delete=models.CASCADE, related_name="audios"
    )
    file = models.FileField(upload_to="uploaded_audios/%Y/%m/%d/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.file.name
