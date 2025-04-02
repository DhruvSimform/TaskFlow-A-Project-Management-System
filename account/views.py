# from django.shortcuts import render
# from rest_framework.permissions import IsAuthenticated
# Create your views here.
import datetime

from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh", None)

        if refresh_token and cache.get(refresh_token) == "blacklisted":
            return Response(
                {"error": "Refresh token has been blacklisted"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return super().post(request, *args, **kwargs)


class LogoutView(APIView):

    def post(self, request):
        try:
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return Response(
                    {"error": "No token Provided"}, status=status.HTTP_404_NOT_FOUND
                )

            access_token = auth_header.split(" ")[1]

            refresh_token = request.data.get("refresh", None)

            if refresh_token:
                refresh_expiration = datetime.timedelta(days=7)
                cache.set(
                    refresh_token,
                    "blacklisted",
                    timeout=int(refresh_expiration.total_seconds()),
                )

            expiration_time = datetime.timedelta(minutes=5)
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
