from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from .models import (
    CampaignProject,
    TranscriptionJob,
    UploadedAudio,
    normalize_windows_path,
    vault_exists,
)
from .tasks import transcribe_job


def _default_vault_base() -> Path:
    """Where campaign vaults live by default (settings.DEFAULT_VAULT_BASE_DIR) — falls back
    to the server's home directory if that folder isn't there (e.g. a different machine)."""
    base = Path(normalize_windows_path(settings.DEFAULT_VAULT_BASE_DIR))
    return base if base.is_dir() else Path.home()


def project_list(request):
    projects = CampaignProject.objects.all()
    return render(
        request,
        "orchestrator/projects.html",
        {"projects": projects, "default_vault_base": str(_default_vault_base())},
    )


def browse_folders(request):
    """In-app folder browser for picking vault_path — server and browser are the same
    machine (single local user), but a web page can never read a real OS filesystem path
    from a native file picker, so this walks the server's filesystem instead."""
    raw_path = normalize_windows_path(request.GET.get("path", "").strip())
    current = Path(raw_path) if raw_path else _default_vault_base()
    if not current.is_dir():
        current = Path.home()

    try:
        subfolders = sorted(
            (p for p in current.iterdir() if p.is_dir() and not p.name.startswith(".")),
            key=lambda p: p.name.lower(),
        )
    except PermissionError:
        subfolders = []

    parent = current.parent if current != current.parent else None

    return render(
        request,
        "orchestrator/_folder_browser.html",
        {
            "current_path": str(current),
            "parent_path": str(parent) if parent else "",
            "subfolders": [{"name": p.name, "path": str(p)} for p in subfolders],
        },
    )


def project_create(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    name = request.POST.get("name", "").strip()
    base_path = normalize_windows_path(request.POST.get("vault_path", "").strip())
    mode = request.POST.get("mode", "new")

    error = None
    if not name or not base_path:
        error = "Nombre y ruta son obligatorios."
    elif not Path(base_path).is_absolute():
        # A relative path resolves against the server process's cwd (the repo root when
        # running via `make run`), silently creating vault folders inside this repo.
        error = "La ruta debe ser absoluta (usa 'Elegir carpeta…' para evitar errores)."

    vault_path = base_path
    if not error and mode == "new":
        # "new" mode: the path picked is the parent folder — the project's own folder is
        # named after it, so the vault lives at <base_path>/<slug(name)>.
        slug = slugify(name)
        if not slug:
            error = "El nombre debe incluir alguna letra o número para poder nombrar la carpeta."
        else:
            vault_path = str(Path(base_path) / slug)

    if not error and CampaignProject.objects.filter(vault_path=vault_path).exists():
        error = "Ya hay un proyecto cargado en esa carpeta."
    elif not error and mode == "existing" and not vault_exists(vault_path):
        error = (
            "Esa ruta no tiene la estructura de un vault (raws/ y campaña/) todavía — "
            "si es la primera vez, usa 'Crear proyecto nuevo'."
        )

    if error:
        projects = CampaignProject.objects.all()
        return render(
            request,
            "orchestrator/projects.html",
            {
                "projects": projects,
                "error": error,
                "default_vault_base": str(_default_vault_base()),
            },
        )

    # CampaignProject.save() ensures raws/ and campaña/{...}/ under vault_path (idempotent):
    # in "existing" mode it touches nothing because they're already there; in "new" mode it
    # creates them.
    CampaignProject.objects.create(name=name, vault_path=vault_path)
    return redirect("orchestrator:project_list")


def project_edit(request, project_id):
    project = get_object_or_404(CampaignProject, pk=project_id)
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    name = request.POST.get("name", "").strip()
    vault_path = normalize_windows_path(request.POST.get("vault_path", "").strip())

    error = None
    if not name or not vault_path:
        error = "Nombre y ruta del vault son obligatorios."
    elif not Path(vault_path).is_absolute():
        error = "La ruta debe ser absoluta (usa 'Elegir carpeta…' para evitar errores)."
    elif (
        CampaignProject.objects.exclude(pk=project.pk)
        .filter(vault_path=vault_path)
        .exists()
    ):
        error = "Ya hay otro proyecto cargado con esa ruta de vault."

    if error:
        jobs = project.jobs.all()
        return render(
            request,
            "orchestrator/project_detail.html",
            {"project": project, "jobs": jobs, "edit_error": error, "editing": True},
        )

    # CampaignProject.save() ensures raws/ and campaña/{...}/ under the (possibly new)
    # vault_path — idempotent, never touches files that already exist.
    project.name = name
    project.vault_path = vault_path
    project.save()
    return redirect("orchestrator:project_detail", project_id=project.pk)


def project_delete(request, project_id):
    """Deletes the CampaignProject row (and its jobs/audios rows via cascade) only —
    never touches the vault on disk nor uploaded audio files."""
    project = get_object_or_404(CampaignProject, pk=project_id)
    if request.method not in ("POST", "DELETE"):
        return HttpResponseBadRequest("Método no permitido")

    project.delete()

    if request.headers.get("HX-Request"):
        return HttpResponse("")
    return redirect("orchestrator:project_list")


def project_detail(request, project_id):
    project = get_object_or_404(CampaignProject, pk=project_id)
    jobs = project.jobs.all()
    return render(
        request, "orchestrator/project_detail.html", {"project": project, "jobs": jobs}
    )


def job_create(request, project_id):
    project = get_object_or_404(CampaignProject, pk=project_id)
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    files = request.FILES.getlist("audios")
    if not files:
        return HttpResponseBadRequest("Hace falta subir al menos un audio.")

    job = TranscriptionJob.objects.create(project=project)
    for order, file in enumerate(files):
        UploadedAudio.objects.create(job=job, file=file, order=order)

    transcribe_job(job.pk)

    return render(request, "orchestrator/_job_row.html", {"job": job})


def job_status(request, job_id):
    job = get_object_or_404(TranscriptionJob, pk=job_id)
    return render(request, "orchestrator/_job_row.html", {"job": job})
