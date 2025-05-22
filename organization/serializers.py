import random
import string

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from account.models import CustomUser

from .models import Department
from .tasks import send_welcome_email


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for admin user to create and update department"""

    class Meta:
        model = Department
        fields = ["id", "department_name", "created_at", "updated_at"]
        extra_kwargs = {
            "created_by": {"read_only": True},
            "updated_at": {"read_only": True},
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for Admin user to registration by Admin , and update the role or department of user"""

    department = serializers.SlugRelatedField(
        slug_field="department_name",
        queryset=Department.objects.all(),
        required=False,
        allow_null=True,
    )

    # password is hidden to set randome password at time of user creation
    password = serializers.HiddenField(default="Root@123")

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "role",
            "password",
            "department",
            "profile_img",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def get_extra_kwargs(self):
        kwargs = super().get_extra_kwargs()

        if self.instance:

            read_only_fields = ["email", "first_name", "last_name", "password"]

            for fields in read_only_fields:
                kwargs[fields] = {"read_only": True}
        return kwargs

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

    def update(self, instance, validated_data):
        validated_data.pop("password", None)
        return super().update(instance, validated_data)


def generate_password(self, length=12):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.SystemRandom().choice(characters) for _ in range(length))
