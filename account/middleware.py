# from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.permissions import IsAuthenticated


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Allow access to these routes without authentication
        allowed_routes = [
            "/api/account/login/",
            "/api/account/token/verify/",
            "/api/account/token/refresh/",
            "/admin/login/",
        ]

        if request.path in allowed_routes:
            return None  # Let the request pass without authentication

        # If user is NOT authenticated
        if not IsAuthenticated:
            if request.path.startswith("/api/"):  # API request
                return None
            else:  # Web/Admin request
                return redirect(reverse("admin:login"))

    def process_response(self, request, response):
        if hasattr(response, "render") and callable(response.render):
            response.render()  # Prevents ContentNotRenderedError
        return response
