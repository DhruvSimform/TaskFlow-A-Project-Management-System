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
    """TaskListCreateView is a view that provides functionality for listing and creating tasks
    associated with a specific project. It supports filtering, searching, and ordering of tasks.
    Attributes:
        permission_classes (list): Specifies the permissions required to access this view.
        serializer_class (Serializer): The serializer class used for task data.
        filter_backends (list): Defines the backends for filtering, searching, and ordering.
        search_fields (list): Fields that can be searched using the search filter.
        filterset_fields (list): Fields that can be filtered using query parameters.
        ordering_fields (list): Fields that can be used for ordering the results.
        ordering (list): Default ordering applied to the results.
    Methods:
        get_queryset():
            Retrieves the queryset of tasks based on the user's role and project association.
            Admins can view all tasks, while Managers/Developers can view tasks they created
            or are collaborators on.
        perform_create(serializer):
            Handles the creation of a new task. It retrieves the project instance using the
            project_id from the URL, checks object-level permissions, and saves the task
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
        """
        Overrides the perform_create method to handle object creation with additional logic.
        This method retrieves the project instance using the provided project_id from the URL
        kwargs, checks object-level permissions for the project, and then saves the serializer
        with the associated project and user information.
        Args:
            serializer (Serializer): The serializer instance containing the validated data.
        Raises:
            Http404: If the project with the given project_id does not exist.
            PermissionDenied: If the user does not have the required permissions for the project.
        Returns:
            The saved instance of the serializer with additional fields populated.
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
    TaskUpdateDeleteView is a view that provides functionality for retrieving, updating,
    and deleting tasks within a project. It enforces permissions based on the user's role
    and their association with the task or project.
    Methods:
        get_permissions():
            Determines the permissions required for each HTTP method.
            Allows GET, PUT, PATCH for Admin, Task Owner, or Collaborators.
            Only Admin or Task Owner can perform DELETE.
        get_queryset():
            Returns a queryset of tasks filtered by the project ID and the user's role.
            Admins can access all tasks in the project, while other users can only access
            tasks they created or are collaborating on.
        get_object():
            Retrieves a specific task object, ensuring it belongs to the specified project.
        perform_update(serializer):
            Automatically sets the `updated_by` field to the current user when a task is updated.
    """

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
    """
    View to manage task collaborators by allowing creation and deletion of collaborators.
    This view supports the following operations:
    - Adding a collaborator to a task (via POST request).
    - Removing a collaborator from a task (via DELETE request).
    Attributes:
        serializer_class (TaskCollaboratorSerializer): The serializer used for task collaborator data.
        permission_classes (list): Permissions required to access this view.
                                   Only admins or task owners are allowed.
    Methods:
        get_queryset():
            Retrieves the queryset of TaskCollaborator objects for the specified task.
            Ensures the task exists under the given project.
        get_object():
            Retrieves a specific TaskCollaborator object based on the provided email.
            Ensures the user exists and is associated with the task.
        perform_create(serializer):
            Handles the creation of a new TaskCollaborator.
            Ensures the task and user exist, and associates the collaborator with the task.
    """

    serializer_class = TaskCollaboratorSerializer
    permission_classes = [IsAdminOrTaskOwner]

    def get_queryset(self):
        """
        Retrieve the queryset of TaskCollaborator objects for a specific task
        under a given project.
        Returns:
            QuerySet: A queryset of TaskCollaborator objects associated with the task.
        """

        project_id = self.kwargs["project_id"]
        task_id = self.kwargs["pk"]

        # Ensure the task exists under the given project
        self.task = get_object_or_404(Task, pk=task_id, project__id=project_id)
        return TaskCollaborator.objects.filter(task=self.task)

    def get_object(self):
        """
        Retrieve an object based on the provided email in the URL.

        This method first fetches a user object using the provided email
        from the URL's keyword arguments. Then, it retrieves an object
        from the queryset associated with the view, filtered by the
        retrieved user.

        Returns:
            object: The retrieved object from the queryset.

        Raises:
            Http404: If no user is found with the provided email or if no
            object is found in the queryset for the retrieved user.
        """

        email = self.kwargs.get("email")
        user = get_object_or_404(CustomUser, email=email)
        return get_object_or_404(self.get_queryset(), user=user)

    def perform_create(self, serializer):
        """
        Overrides the perform_create method to handle custom object creation logic.
        This method retrieves the task and user objects based on the provided
        URL parameters and associates them with the serializer before saving.
        Args:
            serializer (Serializer): The serializer instance containing the
            validated data to be saved.
        Raises:
            Http404: If the Task object with the given task_id and project_id
            does not exist.
            Http404: If the CustomUser object with the given email does not exist.
        Saves:
            The serializer instance with the associated task, user, and the
            current user as the added_by field.
        """

        task_id = self.kwargs["pk"]
        project_id = self.kwargs["project_id"]
        email = self.kwargs.get("email")

        task = get_object_or_404(Task, pk=task_id, project__id=project_id)
        user = get_object_or_404(CustomUser, email=email)

        serializer.save(task=task, user=user, added_by=self.request.user)
