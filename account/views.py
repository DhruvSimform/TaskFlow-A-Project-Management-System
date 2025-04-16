# from django.shortcuts import render
# from rest_framework.permissions import IsAuthenticated
# Create your views here.
import datetime

from django.contrib.auth.tokens import PasswordResetTokenGenerator

# from django.conf import settings
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


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining JWT tokens.
    This view extends the `TokenObtainPairView` to include additional functionality.
    It uses the `TokenObtainPairSerializer` to validate user credentials and generate
    access and refresh tokens. Additionally, it updates the `last_login` field of the
    user upon successful authentication.
    Methods:
        post(request, *args, **kwargs):
            Handles POST requests to validate user credentials, generate tokens, and
            update the user's `last_login` field.
    """

    serializer_class = TokenObtainPairSerializer

    throttle_classes = [LoginThrottlePerHour, LoginThrottlePerMinute]

    def post(self, request, *args, **kwargs):
        # Validate credentials and generate tokens using parent method
        response = super().post(request, *args, **kwargs)

        # Use the serializer to access the validated user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        return response


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
    """
    home to test authentication user tokens
    """

    def get_dashboard_stats(self, user_id):
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
        user = request.user
        stats = self.get_dashboard_stats(user.id)

        print(user)  # Get the authenticated user
        return Response(
            data={
                "message": "Hello!",
                "user_info": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "name": user.name,
                },
                "stats": stats,
            }
        )


class ChangePasswordView(UpdateAPIView):
    throttle_classes = [ChangePasswordThrottle]
    # throttle_scope = 'change_password'
    """
    View for logged-in users to update their password.
    """

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
    throttle_classes = [ResetPasswordThrottle]
    """
    View to handle password reset requests.
    This view allows users to request a password reset by providing their email address.
    If the email is associated with a registered user, a password reset link is generated
    and sent to the user's email.
    Attributes:
        serializer_class (RequestResetPasswordSerializer): The serializer class used for validating input data.
        queryset (list): An empty queryset as this view does not interact with a specific model.
    Methods:
        post(request):
            Handles the POST request to generate a password reset link.
            - Validates the presence of the "email" field in the request data.
            - Checks if a user exists with the provided email.
            - Generates a password reset link containing a unique token and user ID.
            - Sends the reset link to the user's email asynchronously.
            - Returns a success response if the email is sent, or an error response if the user does not exist.
    """

    serializer_class = RequestResetPasswordSerializer
    queryset = []

    def post(self, request):
        user_email = request.data.get("email")
        if not user_email:
            raise ValidationError("Email is not provided")

        try:
            user = CustomUser.objects.get(email=user_email)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "User does not exist with this email ID."},
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
    """
    Handles password reset functionality for users.
    Attributes:
        serializer_class (ResetPasswordSerializer): The serializer class used for validating input data.
        queryset (list): An empty list, as this view does not require a queryset.
    Methods:
        post(request, uidb64, token):
            Handles the POST request to reset the user's password.
            Args:
                request (Request): The HTTP request object containing the password data.
                uidb64 (str): The base64 encoded user ID.
                token (str): The password reset token.
            Raises:
                ValidationError: If the user ID is invalid or passwords do not match.
                AuthenticationFailed: If the token is invalid or expired.
            Returns:
                Response: A success message indicating the password has been reset.
    """

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

        password = request.data.get("password")
        password2 = request.data.get("password2")

        if password != password2:
            raise ValidationError("Passwords do not match.")

        user.set_password(password)
        user.save()

        return Response({"message": "Password has been reset successfully."})
