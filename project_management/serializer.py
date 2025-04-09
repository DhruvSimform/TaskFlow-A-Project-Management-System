from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from organization.serializers import UserRegistrationSerializer

from .models import Project, ProjectCollaborator


class ProjectListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ["id", "name", "description", "status"]


class ProjectCollaboratorSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer(read_only=True)
    added_by = serializers.StringRelatedField()

    class Meta:
        model = ProjectCollaborator
        fields = ["id", "user", "addeed_at", "added_by"]


class ProjectSerializer(serializers.ModelSerializer):
    collaborators = serializers.SerializerMethodField()
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "status",
            "created_by",
            "updated_by",
            "collaborators",
            "created_at",
            "updated_at",
        ]

        read_only_fields = (
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "id",
        )

    def get_collaborators(self, obj):
        collaborators = ProjectCollaborator.objects.filter(project=obj)
        return ProjectCollaboratorSerializer(collaborators, many=True).data


class AddCollaboratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCollaborator
        fields = ["project", "user", "addeed_at", "added_by"]
        read_only_fields = ["project", "user", "addeed_at", "added_by"]

    def validate(self, attrs):
        project = self.context["project"]
        user = self.context["user"]

        if ProjectCollaborator.objects.filter(project=project, user=user).exists():
            raise ValidationError("User is already a collaborator on this project.")

        return attrs

    def create(self, validated_data):
        project = self.context["project"]
        user = self.context["user"]
        added_by = self.context["request"].user

        return ProjectCollaborator.objects.create(
            project=project, user=user, added_by=added_by
        )
