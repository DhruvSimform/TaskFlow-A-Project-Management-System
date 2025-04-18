from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models

from organization.models import Department

from .manager import CustomeUserManager


def email_only_gmail(value):
    """
    Validate that the given email address ends with '@gmail.com'.
    """

    if not value.endswith("@gmail.com"):
        raise ValidationError("only Gmail Address are Allowed")


class Role(models.TextChoices):
    """Text Choices of roles for user"""

    ADMIN = "ADMIN", "Admin"
    MANAGER = "MANAGER", "Manager"
    DEVELOPER = "DEVELOPER", "Developer"


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model extending AbstractBaseUser and PermissionsMixin with email as the username field.
    """

    email = models.EmailField(unique=True, blank=False, validators=[email_only_gmail])
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)
    is_active = models.BooleanField(default=True)  # Can login or not
    is_staff = models.BooleanField(default=False)  # Admin access

    role = models.CharField(choices=Role.choices, max_length=15, default=Role.DEVELOPER)
    profile_img = models.ImageField(upload_to="profile/", blank=True, null=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )

    # Custom manager for email as username filed to use
    objects = CustomeUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "role"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email}"

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
