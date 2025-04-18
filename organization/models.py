from django.db import models


class Department(models.Model):
    """
    Represents a department with a unique name, and tracks creation and update timestamps.
    """

    department_name = models.CharField(max_length=255, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.department_name = self.department_name.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.department_name
