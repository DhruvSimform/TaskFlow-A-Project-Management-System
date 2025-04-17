from rest_framework.permissions import BasePermission


class IsAdminOrCollaborator(BasePermission):
    """
    Permission class to grant access to authenticated users who are either admins or collaborators of the object.
    """

    def has_object_permission(self, request, view, obj):
        is_admin = request.user.role == "ADMIN"
        is_collaborator = obj.collaborators.filter(id=request.user.id).exists()
        return request.user.is_authenticated and (is_admin or is_collaborator)


class IsAdminOrManager(BasePermission):
    """
    Permission class to grant access only to users with 'ADMIN' or 'MANAGER' roles.
    """

    def has_permission(self, request, view):
        return request.user.role == "ADMIN" or request.user.role == "MANAGER"


class IsAdminOrCollaboratingManager(BasePermission):
    """Custom permission to allow access to Admins or Managers collaborating on the project."""

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admins always have access
        if user.role == "ADMIN":
            return True

        # Managers must be collaborators of this project
        if user.role == "MANAGER":
            return obj.collaborators.filter(id=request.user.id).exists()

        return False
