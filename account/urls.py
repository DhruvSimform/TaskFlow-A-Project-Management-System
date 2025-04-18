from django.urls import path

from account import views

# app_name = "accounts"


urlpatterns = [
    # Authentication endpoints
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login"),
    path(
        "token/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"
    ),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # User profile & account actions
    path(
        "change-password/", views.ChangePasswordView.as_view(), name="change_password"
    ),
    path(
        "profile-pic/", views.UpdateProfilePicView.as_view(), name="update_profile_pic"
    ),
    # Password reset flow
    path(
        "request-reset-password/",
        views.GeneratePasswordResetView.as_view(),
        name="request_password_reset",
    ),
    path(
        "request-reset-password/<uidb64>/<token>/",
        views.PasswordResetView.as_view(),
        name="password_reset_confirm",
    ),
    # get dashborad details (Pending task , Totla Project , Completed task by store procedure)
    path("", views.Home.as_view(), name="home"),
]
