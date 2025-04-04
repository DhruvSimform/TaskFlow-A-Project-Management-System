# from django.contrib.auth import get_user_model
from django.db import models

# from account.models import CustomUser


class Department(models.Model):
    department_name = models.CharField(max_length=255, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_department")

    def save(self, *args, **kwargs):
        self.department_name = self.department_name.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.department_name
