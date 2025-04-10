from django.db import models

from account.models import CustomUser

from .mixin import CreatedUpdatedByMixin, DataTimeMixIn

# Project status choices
PROJECT_STATUS = [
    ("PENDING", "Pending"),
    ("IN_PROGRESS", "In Progress"),
    ("COMPLETED", "Completed"),
    ("CLOSED", "Closed"),
]


class ProjectCollaborator(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    addeed_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        CustomUser, on_delete=models.DO_NOTHING, related_name="added_collaborators"
    )
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "project")

    def __str__(self):
        return f"{self.user.email} -> {self.project.name}"


class Project(DataTimeMixIn, CreatedUpdatedByMixin):
    name = models.CharField(
        max_length=255, unique=True, blank=False, null=False, db_index=True
    )
    description = models.TextField()
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default="PENDING")
    is_deleted = models.BooleanField(default=False)
    collaborators = models.ManyToManyField(
        CustomUser,
        related_name="collaborated_projects",
        through="ProjectCollaborator",
        through_fields=("project", "user"),
    )

    def __str__(self):
        return self.name
