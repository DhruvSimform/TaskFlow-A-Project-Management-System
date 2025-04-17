# from django.http import JsonResponse
import logging
import re

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


class AuthMiddleware(MiddlewareMixin):
    """
    Middleware to enforce user authentication for accessing URLs, except for predefined routes.
    """

    def __call__(self, request):
        user_ip = request.META.get("REMOTE_ADDR", "Unknown IP")
        user_agent = request.META.get("HTTP_USER_AGENT", "Unknown User Agent")
        logger.info(
            f"Request from IP: {user_ip}, User Agent: {user_agent}, Path: {request.path}"
        )
        return super().__call__(request)

    def process_request(self, request):
        """
        Handles authentication and token validation for incoming requests.

        This method checks if the request path is in the list of allowed routes that
        do not require authentication. If the request contains an Authorization header
        with a Bearer token, it validates the token and checks if it is blacklisted.
        For unauthenticated users, it redirects to the login page for web/admin requests
        or allows API requests to proceed without authentication.
        """

        allowed_routes = [
            "/api/account/login/",
            "/api/account/token/verify/",
            "/api/account/token/refresh/",
            "/admin/login/",
            "/api/account/request-reset-password/",
        ]

        if (
            request.path in allowed_routes
            or request.path.startswith("/api/account/request-reset-password/")
            or request.path.startswith("/admin/")
        ):
            return None  # Let the request pass without authentication

        # Extract token from the Authorization header
        auth_header = request.headers.get("Authorization", "")
        token_match = re.match(r"Bearer (.+)", auth_header)

        if not token_match:
            return JsonResponse(
                {"error": "Your Token is not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = token_match.group(1)  # Extract token

        # Check if token is blacklisted in Redis
        if cache.get(access_token) == "blacklisted":
            return JsonResponse(
                {"error": "token is invalid"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # If user is NOT authenticated
        if not IsAuthenticated:
            if request.path.startswith("/api/"):  # API request
                return None
            else:  # Web/Admin request
                return redirect(reverse("admin:login"))
