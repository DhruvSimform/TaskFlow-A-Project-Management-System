from rest_framework import serializers

from account.models import CustomUser

from .models import Task, TaskCollaborator


class TaskCollaboratorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Optional: For better readability
    addedby = serializers.StringRelatedField()

    class Meta:
        model = TaskCollaborator
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    subtask = serializers.SerializerMethodField()
    collaborators = serializers.SerializerMethodField()
    also_collaborator = serializers.BooleanField(write_only=True, required=False)

    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)

    # Accept collaborator user IDs in POST (write-only)
    collaborator_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ("created_by", "updated_by", "completed_date")

    def create(self, validated_data):
        request_user = self.context["request"].user
        collaborator_ids = validated_data.pop("collaborator_ids", [])
        also_collaborator = validated_data.pop("also_collaborator", False)

        # Create task
        a = CustomUser.objects.get(pk=1)
        task = Task.objects.create(created_by=a, updated_by=a, **validated_data)

        # Add listed collaborators
        for uid in collaborator_ids:
            user = CustomUser.objects.get(pk=uid)
            TaskCollaborator.objects.create(task=task, user=user, added_by=a)

        # Add manager (creator) as collaborator if they checked the box
        if also_collaborator and request_user.id not in collaborator_ids:
            TaskCollaborator.objects.create(task=task, user=a, added_by=a)

        return task

    def get_collaborators(self, obj):
        collaborators = TaskCollaborator.objects.filter(task=obj)
        return TaskCollaboratorSerializer(collaborators, many=True).data

    def get_subtask(self, obj):
        subtask = obj.sub_tasks.all()
        return TaskSerializer(subtask, many=True).data

    def validate(self, data):
        # try:
        #     Merge existing instance data if updating
        cleaned_data = data.copy()
        cleaned_data.pop("also_collaborator", None)  # safely remove it if it exists
        instance = (
            Task(**{**self.instance.__dict__, **cleaned_data})
            if self.instance
            else Task(**cleaned_data)
        )
        instance.clean()

    # except DjangoValidationError as e:
    # pass
    #     if hasattr(e, 'message_dict'):
    #         raise serializers.ValidationError(e.message_dict)
    #     else:
    #         raise serializers.ValidationError({"non_field_errors": e.messages})
    # return data
