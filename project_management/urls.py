from django.urls import path

from . import views

urlpatterns = [
    path("", views.Home.as_view(), name="projecthome"),
    # url to list all projects and and create project
    path(
        "project/", views.ProjectView.as_view(), name="project"
    ),  # Admin can view all Projects , Manager and Devlopers can only see project in which they are as collaboraters , and project create can only be done by admin or manager role dev
    # url to see project detail of specifi project (This can be accesed by admin or user who is added in collaborater of that project)
    path("project/<int:pk>", views.ProjectDetailsUpdateRetriveDeleteView.as_view()),
    # Url to add collaborate to project (only admin or creater manager of that project can do)
    path(
        "project/<int:pk>/collaborator/<str:email>", views.CollaboratorView.as_view()
    ),  # working on this
]

# collaborators
