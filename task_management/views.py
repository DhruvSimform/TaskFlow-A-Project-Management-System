from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
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
    """
    View for listing and creating tasks with filtering, searching, and ordering support.
    """

    permission_classes = [IsAdminOrCollaborator]
    serializer_class = TaskSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = ["title", "description", "project__name", "status", "priority"]

    #  Fields you can filter with ?status=C&priority=H
    filterset_fields = ["status", "priority", "project", "created_by"]

    #  Fields you can order by ?ordering=start_date or ?ordering=-priority
    ordering_fields = ["start_date", "due_date", "priority", "status", "title"]
    ordering = ["start_date"]  # Default ordering

    def get_queryset(self):
        """
        Retrieve the queryset of tasks based on the user's role and project ID.
        """

        user = self.request.user
        project_id = self.kwargs.get("project_id")
        if user.role == "ADMIN":
            return Task.objects.filter(project__id=project_id)
        return Task.objects.filter(
            (Q(created_by=user) | Q(collaborators=user)) & Q(project__id=project_id)
        ).distinct()

    def perform_create(self, serializer):
        """
        Handles the creation of an object with project association and permissions check.
        """

        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, id=project_id)

        # Check object-level permission for the project
        self.check_object_permissions(self.request, project)

        return serializer.save(
            created_by=self.request.user, updated_by=self.request.user, project=project
        )


class TaskUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    """
    TaskUpdateDeleteView handles retrieving, updating, and deleting tasks with role-based permissions and project association checks.
    """

    serializer_class = TaskSerializer

    def get_permissions(self):
        """
        Determine and return the appropriate permissions based on the request method.
        """

        if self.request.method in ["GET", "PUT", "PATCH"]:
            return [IsAdminOrTaskOwnerOrCollaborator()]
        return [IsAdminOrTaskOwner()]

    def get_queryset(self):
        """
        Retrieve the queryset of tasks based on the user's role and project ID.
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
    """
    View to manage task collaborators by allowing creation and deletion of collaborators.
    """

    serializer_class = TaskCollaboratorSerializer
    permission_classes = [IsAdminOrTaskOwner]

    def get_queryset(self):
        """Retrieve TaskCollaborator queryset for a specific task in a project."""

        project_id = self.kwargs["project_id"]
        task_id = self.kwargs["pk"]

        # Ensure the task exists under the given project
        self.task = get_object_or_404(Task, pk=task_id, project__id=project_id)
        return TaskCollaborator.objects.filter(task=self.task)

    def get_object(self):
        """Retrieve an object filtered by user email from the queryset."""

        email = self.kwargs.get("email")
        user = get_object_or_404(CustomUser, email=email)
        return get_object_or_404(self.get_queryset(), user=user)

    def perform_create(self, serializer):
        """
        Handles custom object creation by associating task, user, and added_by fields with the serializer.
        """

        task_id = self.kwargs["pk"]
        project_id = self.kwargs["project_id"]
        email = self.kwargs.get("email")

        task = get_object_or_404(Task, pk=task_id, project__id=project_id)
        user = get_object_or_404(CustomUser, email=email)

        serializer.save(task=task, user=user, added_by=self.request.user)
