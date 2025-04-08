from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import CustomUser

user = get_user_model()


class UpdateUserPasswordSerializer(serializers.Serializer):
    """
    serializer for logged in user so he/she can update his/her password only
    """

    new_password = serializers.CharField(required=True, write_only=True)

    def valid_new_password(value):
        validate_password(value)
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class ProfilePicSerializer(serializers.ModelSerializer):
    """
    serializer for logged user to update his profile pic
    """

    class Meta:
        model = CustomUser
        fields = ["profile_img"]
