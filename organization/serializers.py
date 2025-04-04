from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from account.models import CustomUser

from .models import Department
from .tasks import send_welcome_email

# import random
# import string


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "department_name", "created_at", "updated_at"]
        extra_kwargs = {"created_by": {"read_only": True}}


# class AllocateUserToDepartmentSerializer(serializers.Serializer):
#     department = serializers.PrimaryKeyRelatedField(quer)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration by Admin"""

    department = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    password = serializers.HiddenField(default="Root@123")

    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "role", "password", "department"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        """Ensure password meets Django's validation rules"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        """Generate a strong password if not provided and create a user"""
        password = validated_data.pop("password", None)
        if not password:
            password = self.generate_password()

        user = CustomUser(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()

        # Call Celery task to send an email
        send_welcome_email.delay(user.email, user.first_name, password)
        return user

    # def generate_password(self, length=12):
    #     """Generate a secure random password"""
    #     # characters = string.ascii_letters + string.digits + string.punctuation
    #     return "Root@123"
