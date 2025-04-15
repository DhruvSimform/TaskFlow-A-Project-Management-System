from django.urls import path

from . import views

urlpatterns = [
    # login api for getting access and refresh token
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login"),
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
    # api for reset password for user
    path(
        "request-reset-password/",
        views.GeneratePasswordResetView.as_view(),
        name="genrate_password_reset_url",
    ),
    path(
        "request-reset-password/<uidb64>/<token>/",
        views.PasswordResetView.as_view(),
        name="reset-password",
    ),
    # api to to just test account app's functinality for auth
    path("", views.Home.as_view(), name="home"),
]
