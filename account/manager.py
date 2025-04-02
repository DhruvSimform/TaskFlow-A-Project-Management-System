from django.contrib.auth.models import BaseUserManager


class CustomeUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Create a Normal user with email and password"""

        if not email:
            raise ValueError("The Email Filed is Must Required")

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
