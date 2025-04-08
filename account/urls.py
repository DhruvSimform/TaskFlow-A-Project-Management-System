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
    # logout api to blacklit the access and refresh token
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # API for logged in user can update his/her password
    path(
        "change-password/", views.ChangePasswordView.as_view(), name="change_password"
    ),
    # api for logged in user to change his profile pic
    path("profile-pic/", views.UpdateProfilePicView.as_view()),
    # api to to just test account app's functinality for auth
    path("", views.Home.as_view(), name="home"),
]
