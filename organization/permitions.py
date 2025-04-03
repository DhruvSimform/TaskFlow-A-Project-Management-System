from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Custom permission check to ensure the API is accessible only to users with the 'Admin' role.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"
