from django.urls import path

from . import views

urlpatterns = [
    # User endpoints
    path(
        "users/",
        views.UserView.as_view(),
        name="user-list-create",  # View all users and create a new user
    ),
    path(
        "users/<str:email>/",
        views.UserUpdateRetriveView.as_view(),
        name="user-retrieve-update",  # Retrieve or update a user by email
    ),
    # Department endpoints
    path(
        "departments/",
        views.DepartmentView.as_view(),
        name="department-list-create",  # View all departments and create a new department
    ),
    path(
        "departments/<int:pk>/",
        views.DepartmentUpdateRetriveView.as_view(),
        name="department-retrieve-update",  # Retrieve or update a department by ID
    ),
]
