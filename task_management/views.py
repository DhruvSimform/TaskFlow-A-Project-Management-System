from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import CustomUser
from project_management.models import Project
from project_management.permitions import IsAdminOrCollaborator
from task_management.models import TaskCollaborator
from task_management.permitions import (
    IsAdminOrTaskOwner,
    IsAdminOrTaskOwnerOrCollaborator,
)

from .models import Task
from .serializer import TaskCollaboratorSerializer, TaskSerializer

# Create your views here.


class Home(APIView):

    def get(self, *args, **kwargs):
        return Response({"Message": "Hello Task Management APP URL is working"})


class TaskListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminOrCollaborator]
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Admin can view all tasks.
        Manager/Developer can view tasks they created or are collaborators on.
        """
        user = self.request.user
        project_id = self.kwargs.get("project_id")
        if user.role == "ADMIN":
            return Task.objects.filter(project__id=project_id)
        return Task.objects.filter(
            (Q(created_by=user) | Q(collaborators=user)) & Q(project__id=project_id)
        ).distinct()

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, id=project_id)

        # Check object-level permission for the project
        self.check_object_permissions(self.request, project)

        return serializer.save(
            created_by=self.request.user, updated_by=self.request.user, project=project
        )


class TaskUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    def get_permissions(self):
        """
        Allow GET, PUT, PATCH for Admin/Owner/Collaborators.
        Only Admin/Owner can DELETE.
        """
        if self.request.method in ["GET", "PUT", "PATCH"]:
            return [IsAdminOrTaskOwnerOrCollaborator()]
        return [IsAdminOrTaskOwner()]

    def get_queryset(self):
        """
        Filter tasks by project and user role.
        """
        user = self.request.user
        project_id = self.kwargs["project_id"]

        if user.role == "ADMIN":
            return Task.objects.filter(project__id=project_id)

        return Task.objects.filter(
            Q(created_by=user) | Q(collaborators=user), project__id=project_id
        ).distinct()

    def get_object(self):
        """
        Ensures the task belongs to the specified project.
        """
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs["pk"])

    def perform_update(self, serializer):
        """
        Auto-set `updated_by` to current user on update.
        """
        serializer.save(updated_by=self.request.user)


class ManageTaskCollaboratorView(CreateAPIView, DestroyAPIView):
    serializer_class = TaskCollaboratorSerializer
    permission_classes = [IsAdminOrTaskOwner]

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        task_id = self.kwargs["pk"]

        # Ensure the task exists under the given project
        self.task = get_object_or_404(Task, pk=task_id, project__id=project_id)
        return TaskCollaborator.objects.filter(task=self.task)

    def get_object(self):
        email = self.kwargs.get("email")
        user = get_object_or_404(CustomUser, email=email)
        return get_object_or_404(self.get_queryset(), user=user)

    def perform_create(self, serializer):
        task_id = self.kwargs["pk"]
        project_id = self.kwargs["project_id"]
        email = self.kwargs.get("email")

        task = get_object_or_404(Task, pk=task_id, project__id=project_id)
        user = get_object_or_404(CustomUser, email=email)

        serializer.save(task=task, user=user, added_by=self.request.user)
