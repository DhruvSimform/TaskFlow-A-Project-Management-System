from django.urls import path

from . import views

urlpatterns = [
    path("", views.Home.as_view(), name="task_home"),
    path("task/", views.TaskListCreateView.as_view(), name="task"),
    path("task/<int:pk>", views.TaskUpdateDeleteView.as_view(), name="task_details"),
]
