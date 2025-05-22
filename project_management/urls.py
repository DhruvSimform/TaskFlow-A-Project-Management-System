from django.urls import path

from . import views

urlpatterns = [
    # Project home - basic health check or welcome view
    path("", views.Home.as_view(), name="project-home"),
    # List all projects / Create a new project
    # - Admin: Can view all projects
    # - Manager/Developer: Can view only projects they collaborate on
    # - Create: Only Admins or Managers
    path("projects/", views.ProjectView.as_view(), name="project-list-create"),
    # Retrieve, update, or delete a specific project
    # - Access: Admin or a collaborator of the project
    path(
        "projects/<int:pk>/",
        views.ProjectDetailsUpdateRetriveDeleteView.as_view(),
        name="project-detail-update-delete",
    ),
    # Add a collaborator to a specific project
    # - Only Admin or the Manager who is collabrators the project can perform this
    path(
        "projects/<int:pk>/collaborators/<str:email>/",
        views.CollaboratorView.as_view(),
        name="project-add-collaborator",
    ),
]
