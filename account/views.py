import datetime
import logging

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from account.models import CustomUser
from account.serializers import (
    ProfilePicSerializer,
    RequestResetPasswordSerializer,
    ResetPasswordSerializer,
    UpdateUserPasswordSerializer,
)
from account.tasks import send_password_reset_email
from account.throttle import (
    ChangePasswordThrottle,
    LoginThrottlePerHour,
    LoginThrottlePerMinute,
    RefreshTokenThrottle,
    ResetPasswordThrottle,
)

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining JWT tokens with added functionality.
    Updates the user's `last_login` field upon successful authentication.
    """

    serializer_class = TokenObtainPairSerializer

    throttle_classes = [LoginThrottlePerHour, LoginThrottlePerMinute]

    def post(self, request, *args, **kwargs):
        logger.info("Attempting to authenticate user.")
        try:
            # Validate credentials and generate tokens using parent method
            response = super().post(request, *args, **kwargs)

            # Use the serializer to access the validated user
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.user
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            logger.info(f"User {user.email} authenticated successfully.")
            return response
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise


class CustomTokenRefreshView(TokenRefreshView):
    """Handles token refresh requests and checks if the refresh token is blacklisted."""

    throttle_classes = [RefreshTokenThrottle]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh", None)

        if refresh_token and cache.get(refresh_token) == "blacklisted":
            return Response(
                {"error": "Refresh token has been blacklisted"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """
    Handles blacklisting of access and refresh tokens during user logout to prevent further use of these tokens.
    """

    def post(self, request):
        try:
            auth_header = request.headers.get("Authorization", None)

            if not auth_header or not auth_header.startswith("Bearer "):
                return Response(
                    {"error": "Invalid or missing Authorization header"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            access_token = auth_header.split(" ")[1]

            refresh_token = request.data.get("refresh", None)

            if refresh_token:
                refresh_expiration = datetime.timedelta(hours=5)
                cache.set(
                    refresh_token,
                    "blacklisted",
                    timeout=int(refresh_expiration.total_seconds()),
                )

            expiration_time = datetime.timedelta(minutes=60)
            cache.set(
                access_token,
                "blacklisted",
                timeout=int(expiration_time.total_seconds()),
            )

            return Response({"message": "Successfully logged out User"})
        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class Home(APIView):
    """Home view to test user authentication tokens and fetch dashboard statistics."""

    def get_dashboard_stats(self, user_id):
        """Fetches dashboard stats for the user via a stored procedure."""
        with connection.cursor() as cursor:
            cursor.callproc("get_user_dashboard_stats", [user_id])
            result = cursor.fetchone()
            return {
                "total_projects": result[0],
                "completed_projects": result[1],
                "pending_tasks": result[2],
                "due_tasks": result[3],
            }

    def get(self, request, *args, **kwargs):
        """Handle GET request to fetch user info and dashboard stats."""

        user = request.user
        stats = self.get_dashboard_stats(user.id)

        return Response(
            data={
                "message": "Welcome to your dashboard!",
                "user_info": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "name": user.name,
                },
                "stats": stats,
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(UpdateAPIView):
    """
    API view to allow logged-in users to change their password.
    """

    throttle_classes = [ChangePasswordThrottle]

    serializer_class = UpdateUserPasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()

        serializer = self.get_serializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {"message": "Your Password is changed successfully!"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfilePicView(UpdateAPIView):
    """
    View for logged-in users to update their profile picture.
    This view allows users to upload or update their profile picture.
    If not set by the user or admin, the profile picture remains None by default.
    """

    serializer_class = ProfilePicSerializer

    def get_object(self):
        return self.request.user


class GeneratePasswordResetView(GenericAPIView):
    """
    Handles password reset requests by validating email and sending a reset link.
    """

    throttle_classes = [ResetPasswordThrottle]
    serializer_class = RequestResetPasswordSerializer
    queryset = []

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_email = serializer.validated_data["email"]

        try:
            user = CustomUser.objects.get(email=user_email)
        except CustomUser.DoesNotExist:
            return Response(
                {"message": "User does not exist with this email ID."},
                status=status.HTTP_404_NOT_FOUND,
            )

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)

        reset_link = f"http://127.0.0.1:8000/api/account/request-reset-password/{uidb64}/{token}/"
        send_password_reset_email.delay(user.email, reset_link)

        return Response(
            {"message": "Reset password email has been sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetView(GenericAPIView):
    throttle_classes = [ResetPasswordThrottle]
    """Handles password reset functionality for users by validating input data, decoding user ID, verifying token, and updating the password if valid."""

    serializer_class = ResetPasswordSerializer
    queryset = []

    def post(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise ValidationError("Invalid user ID")

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise AuthenticationFailed("Invalid or expired token.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data["password1"]
        password2 = serializer.validated_data["password2"]

        if password != password2:
            raise ValidationError("Passwords do not match.")

        user.set_password(password)
        user.save()

        return Response({"message": "Password has been reset successfully."})
