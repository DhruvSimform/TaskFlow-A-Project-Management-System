from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views

urlpatterns = [
    # login api for getting access and refresh token
    path("login/", TokenObtainPairView.as_view(), name="login"),
    # api for getting new access token by refresh token
    path(
        "token/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"
    ),
    # path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # logout api to blacklit the access and refresh token
    path("logout/", views.LogoutView.as_view()),
    path("", views.Home.as_view(), name="home"),
]
