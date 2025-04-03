# from django.shortcuts import render
# from rest_framework.permissions import IsAuthenticated
# Create your views here.
import datetime

# from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import UpdateUserPasswordSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """Handles token refresh requests and checks if the refresh token is blacklisted."""

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

    def get(self, request, *args, **kwargs):
        user = request.user  # Get the authenticated user
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
            }
        )


class ChangePasswordView(UpdateAPIView):
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
