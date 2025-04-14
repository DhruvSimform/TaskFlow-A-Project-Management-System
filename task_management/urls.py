from django.urls import path

from . import views

urlpatterns = [
    path("", views.Home.as_view(), name="task_home"),
    # to view and create task or sub task
    path("<int:project_id>/tasks/", views.TaskListCreateView.as_view(), name="task"),
    # to retrive specifc task and perofre edit , delete
    path(
        "<int:project_id>/tasks/<int:pk>",
        views.TaskUpdateDeleteView.as_view(),
        name="task_details",
    ),
    # to remove user from task collabotor
    path(
        "<int:project_id>/tasks/<int:pk>/<str:email>",
        views.ManageTaskCollaboratorView.as_view(),
        name="manage_task_collaborator",
    ),
]
