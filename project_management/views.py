from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.exceptions import NotFound
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import CustomUser
from organization.permitions import IsAdminUser

from .models import Project, ProjectCollaborator
from .permitions import (
    IsAdminOrCollaboratingManager,
    IsAdminOrCollaborator,
    IsAdminOrManager,
)
from .serializer import (
    AddCollaboratorSerializer,
    ProjectListSerializer,
    ProjectSerializer,
)


# Create your views here.
class Home(APIView):
    def get(self, request):
        data = {"message": "Hello this app is working"}
        return Response(data=data, status=status.HTTP_200_OK)


class ProjectView(ListCreateAPIView):
    serializer_class = ProjectListSerializer
    queryset = Project.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    # Enable filtering by status only
    filterset_fields = ["status"]

    # Enable search on name and description
    search_fields = ["name", "description"]

    ordering_fields = ["last_updated", "status"]
    ordering = ["-last_updated", "status"]

    def get_queryset(self):
        if self.request.user.role == "ADMIN":
            return Project.objects.all()
        return Project.objects.filter(collaborators=self.request.user)

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrManager()]
        else:
            return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)


class ProjectDetailsUpdateRetriveDeleteView(RetrieveUpdateDestroyAPIView):

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [IsAdminOrCollaborator]
        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [IsAdminOrManager]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class CollaboratorView(CreateAPIView, DestroyAPIView):
    permission_classes = [IsAdminOrCollaboratingManager]
    serializer_class = AddCollaboratorSerializer

    def get_object(self):
        return self.get_project()

    def get_project(self):
        project = get_object_or_404(Project, pk=self.kwargs["pk"], is_deleted=False)
        self.check_object_permissions(self.request, project)
        return project

    def get_user(self):
        email = self.kwargs.get("email")
        if not email:
            raise NotFound("Email parameter is required.")
        return get_object_or_404(CustomUser, email=email, is_active=True)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"project": self.get_project(), "user": self.get_user()})
        return context

    def perform_destroy(self, request, *args, **kwargs):
        project = self.get_project()
        user = self.get_user()

        collaborator = ProjectCollaborator.objects.filter(
            project=project, user=user
        ).first()
        if not collaborator:
            raise NotFound("User is not a collaborator on this project.")
        collaborator.delete()
