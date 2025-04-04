from django.urls import path

from . import views

urlpatterns = [
    path("create-user/", views.UserView.as_view(), name="create_user"),
    path(
        "create-department/", views.DepartmentView.as_view(), name="create_department"
    ),
]
