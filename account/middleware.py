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
    AuthMiddleware is a custom Django middleware that enforces user authentication for incoming requests.

    This middleware performs the following tasks:
    1. Logs the IP address, user agent, and request path for every incoming request.
    2. Allows requests to predefined routes (e.g., login, token verification, password reset) to bypass authentication.
    3. Extracts and validates the Bearer token from the Authorization header for protected routes.
    4. Checks if the token is blacklisted using a Redis cache.
    5. Redirects unauthenticated web/admin users to the login page, while allowing unauthenticated API requests to proceed.

    Key Features:
    - Supports both web and API authentication flows.
    - Ensures secure access by validating tokens and preventing the use of blacklisted tokens.
    - Provides flexibility by allowing specific routes to bypass authentication.

    Attributes:
    - allowed_routes: A list of predefined routes that do not require authentication.

    Methods:
    - __call__: Logs request metadata and delegates processing to the parent middleware.
    - process_request: Handles the core authentication logic, including token validation and route-based access control.
    """

    def __call__(self, request):
        user_ip = request.META.get("REMOTE_ADDR", "Unknown IP")
        user_agent = request.META.get("HTTP_USER_AGENT", "Unknown User Agent")
        logger.info(
            f"Request from IP: {user_ip}, User Agent: {user_agent}, Path: {request.path}"
        )
        return super().__call__(request)

    def process_request(self, request):

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
