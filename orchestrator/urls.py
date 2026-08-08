from django.urls import path

from . import views

app_name = "orchestrator"

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("projects/browse-folders/", views.browse_folders, name="browse_folders"),
    path("projects/create/", views.project_create, name="project_create"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
    path(
        "projects/<int:project_id>/edit/",
        views.project_edit,
        name="project_edit",
    ),
    path(
        "projects/<int:project_id>/delete/",
        views.project_delete,
        name="project_delete",
    ),
    path(
        "projects/<int:project_id>/jobs/create/",
        views.job_create,
        name="job_create",
    ),
    path("jobs/<int:job_id>/status/", views.job_status, name="job_status"),
]
