from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError

from account.models import CustomUser

from .models import Task, TaskCollaborator


class TaskCollaboratorSerializer(serializers.ModelSerializer):
    """
    Serializer for TaskCollaborator model with all fields and read-only constraints on specific fields.
    """

    user = serializers.StringRelatedField()  # Optional: For better readability
    added_by = serializers.StringRelatedField()

    class Meta:
        model = TaskCollaborator
        fields = "__all__"
        read_only_fields = ("task", "added_by", "user", "id")


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model, handling creation, validation, and nested data for subtasks and collaborators.
    """

    subtask = serializers.SerializerMethodField()
    collaborators = serializers.SerializerMethodField()
    also_collaborator = serializers.BooleanField(write_only=True, required=False)

    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)

    # Accept collaborator email addresses in POST (write-only)
    collaborator_emails = serializers.ListField(
        child=serializers.EmailField(), write_only=True, required=False
    )

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = (
            "created_by",
            "updated_by",
            "completed_date",
            "created_at",
            "updated_at",
            "project",
        )

    def create(self, validated_data):
        """
        Creates a new task, assigns collaborators based on provided email addresses,
        and optionally adds the creator as a collaborator.
        """

        request_user = self.context[
            "request"
        ].user  # Trigger background tasks after saving the model

        collaborator_emails = validated_data.pop("collaborator_emails", [])
        also_collaborator = validated_data.pop("also_collaborator", False)
        print(collaborator_emails)
        # Create task
        task = Task.objects.create(**validated_data)

        # Add collaborators based on email addresses
        for email in collaborator_emails:
            try:
                user = CustomUser.objects.get(email=email)  # Look up by email
                TaskCollaborator.objects.create(
                    task=task, user=user, added_by=request_user
                )
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(
                    f"User with email {email} does not exist."
                )

        # Add manager (creator) as collaborator if they checked the box
        if also_collaborator and request_user.email not in collaborator_emails:
            TaskCollaborator.objects.create(
                task=task, user=request_user, added_by=request_user
            )

        return task

    def get_collaborators(self, obj):
        collaborators = TaskCollaborator.objects.filter(task=obj)
        return TaskCollaboratorSerializer(collaborators, many=True).data

    def get_subtask(self, obj):
        subtask = obj.sub_tasks.all()
        return TaskSerializer(subtask, many=True, read_only=True).data

    def validate(self, data):
        cleaned_data = data.copy()
        cleaned_data.pop("also_collaborator", None)
        cleaned_data.pop("collaborator_emails", None)

        try:
            instance = Task(**cleaned_data)
            instance.clean()  # Perform model-level validation
        except DjangoValidationError as e:
            raise DRFValidationError(
                e.message_dict
                if hasattr(e, "message_dict")
                else {"non_field_errors": e.messages}
            )

        return data  # return original data, not cleaned_data
