from django.contrib.auth.models import BaseUserManager


class CustomeUserManager(BaseUserManager):
    """
    Custom user manager for handling user creation and superuser creation with email and additional fields.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create a Normal user with email and password"""

        if not email:
            raise ValueError("The Email Filed is Must Required")
        if not extra_fields.get("first_name"):
            raise ValueError("The First Name field is required")
        if not extra_fields.get("last_name"):
            raise ValueError("the last name field is required")
        if not extra_fields.get("role"):
            raise ValueError("role must be provide")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create Superuser(Admin) with Full permitions"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)
