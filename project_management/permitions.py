from rest_framework.permissions import BasePermission


class IsAdminOrCollaborator(BasePermission):
    def has_object_permission(self, request, view, obj):
        is_admin = request.user.role == "ADMIN"
        is_collaborator = obj.collaborators.filter(id=request.user.id).exists()
        return request.user.is_authenticated and (is_admin or is_collaborator)


class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "ADMIN" or request.user.role == "MANAGER"


class IsAdminOrCollaboratingManager(BasePermission):
    """
    Allows access if user is:
    - An Admin (always)
    - A Manager who is a collaborator of the project (obj)
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admins always have access
        if user.role == "ADMIN":
            return True

        # Managers must be collaborators of this project
        if user.role == "MANAGER":
            return obj.collaborators.filter(id=request.user.id).exists()

        return False
