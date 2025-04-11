from django.urls import path

from . import views

urlpatterns = [
    path("", views.Home.as_view(), name="task_home"),
    # to view and create task or sub task
    path("task/", views.TaskListCreateView.as_view(), name="task"),
    # to retrive specifc task and perofre edit , delete
    path("task/<int:pk>", views.TaskUpdateDeleteView.as_view(), name="task_details"),
]
