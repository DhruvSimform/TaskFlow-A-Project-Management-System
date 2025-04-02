from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView

from . import views

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path(
        "token/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"
    ),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("logout/", views.LogoutView.as_view()),
    path("", views.Home.as_view(), name="home"),
]
