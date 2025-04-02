from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models

from .manager import CustomeUserManager


def email_only_gmail(value):
    if not value.endswith("@gmail.com"):
        raise ValidationError("only Gmail Address are Allowed")


class CustomUser(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("MANAGER", "Manager"),
        ("DEVELOPER", "Developer"),
    ]

    email = models.EmailField(unique=True, blank=False, validators=[email_only_gmail])
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)  # Can login or not
    is_staff = models.BooleanField(default=False)  # Admin access

    role = models.CharField(choices=ROLE_CHOICES, max_length=15, default="DEVELOPER")
    profile_img = models.ImageField(upload_to="profile/", blank=True, null=True)

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
