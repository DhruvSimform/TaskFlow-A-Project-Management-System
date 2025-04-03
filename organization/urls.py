from django.urls import path

from . import views

urlpatterns = [
    path("create-user/", views.CreateUserView.as_view(), name="create_user"),
]
