from rest_framework.permissions import BasePermission


class IsAdminOrTaskOwner(BasePermission):
    """
    Allows access to Admin users or the user who created the Task.
    """

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user or request.user.role == "ADMIN"


class IsAdminOrTaskOwnerOrCollaborator(BasePermission):
    """
    Allows access to Admins, Task creator, or Task collaborators.
    """

    def has_object_permission(self, request, view, obj):
        return (
            obj.created_by == request.user
            or obj.collaborators.filter(id=request.user.id).exists()
            or request.user.role == "ADMIN"
        )
