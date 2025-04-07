from django.urls import path

from . import views

urlpatterns = [
    path("user/", views.UserView.as_view(), name="create_user"),
    path(
        "user/<str:email>/", views.UserUpdateRetriveView.as_view(), name="create_user"
    ),
    path("department/", views.DepartmentView.as_view(), name="department_list_create"),
    path(
        "department/<int:pk>/",
        views.DepartmentUpdateRetriveView.as_view(),
        name="department_detail",
    ),
]
