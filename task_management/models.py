from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from account.models import CustomUser
from project_management.mixin import DataTimeMixIn


class TaskStatus(models.TextChoices):
    PENDING = "P", "Pending"
    IN_PROGRESS = "I", "In Progress"
    COMPLETED = "C", "Completed"
    OVERDUE = "O", "Overdue"
    ON_HOLD = "H", "On Hold"
    CANCELLED = "X", "Cancelled"


class TaskPriority(models.TextChoices):
    HIGH = "H", "High"
    MEDIUM = "M", "Medium"
    LOW = "L", "Low"


class TaskCollaborator(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task = models.ForeignKey("Task", on_delete=models.CASCADE)
    added_by = models.ForeignKey(
        CustomUser, on_delete=models.DO_NOTHING, related_name="task_added_collaborators"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} -> {self.task}"


# Field-level validators
def validate_start_date(value):
    pass
    # if value.date() < timezone.now().date():
    #     raise ValidationError("Start Date cannot be in the past.")


def validate_due_date(value):
    if value.date() < timezone.now().date():
        raise ValidationError("Due Date cannot be in the past.")


class Task(DataTimeMixIn):
    title = models.CharField(max_length=255)
    description = models.TextField(null=False, blank=False)

    collaborators = models.ManyToManyField(
        CustomUser,
        related_name="collaborated_tasks",
        through=TaskCollaborator,
        through_fields=("task", "user"),
    )

    parent_task = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="sub_tasks",
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=2, choices=TaskStatus.choices, default=TaskStatus.PENDING
    )

    priority = models.CharField(
        max_length=1, choices=TaskPriority.choices, default=TaskPriority.MEDIUM
    )

    start_date = models.DateTimeField(
        null=False, blank=False, default=timezone.now, validators=[validate_start_date]
    )
    due_date = models.DateTimeField(
        null=True, blank=True, validators=[validate_due_date]
    )
    completed_date = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        CustomUser, on_delete=models.DO_NOTHING, related_name="created_tasks"
    )
    updated_by = models.ForeignKey(
        CustomUser, on_delete=models.DO_NOTHING, related_name="updated_tasks"
    )

    class Meta:
        ordering = ["start_date", "priority"]
        get_latest_by = "start_date"

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def clean(self):
        # Start/Due date logic
        if self.start_date and self.due_date and self.start_date > self.due_date:
            raise ValidationError("Start Date cannot be after Due Date.")

        # Parent task constraints
        if self.parent_task:
            # if self.parent_task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            #     raise ValidationError("Cannot create a sub-task for a completed or cancelled parent task.")

            if self.parent_task.parent_task:
                raise ValidationError("Sub task of Sub task can't create")

            if (
                self.parent_task.start_date
                and self.start_date
                and self.parent_task.start_date > self.start_date
            ):
                raise ValidationError("Task cannot start before its parent task.")

            if (
                self.parent_task.due_date
                and self.start_date
                and self.parent_task.due_date < self.start_date
            ):
                raise ValidationError("Task cannot start after parent task's Due Date.")

            if (
                self.parent_task.due_date
                and self.due_date
                and self.parent_task.due_date < self.due_date
            ):
                raise ValidationError(
                    "Sub-task Due Date cannot exceed parent task's Due Date."
                )

        # if self.completed_date:
        #     if self.completed_date < self.start_date:
        #         raise ValidationError("Completed Date cannot be before Start Date.")
        #     if self.due_date and self.completed_date > self.due_date:
        #         raise ValidationError("Completed Date cannot be after Due Date.")

    def save(self, *args, **kwargs):
        print("== Task Save Called ==")
        self.full_clean()

        if self.status == TaskStatus.COMPLETED and not self.completed_date:
            self.completed_date = timezone.now()

        super().save(*args, **kwargs)

        # ⬇️ Lazy import to avoid circular import
        if self.parent_task_id:
            from task_management.tasks import check_and_complete_parent_task

            print("hii")
            check_and_complete_parent_task.delay(self.id)

        if self.status == TaskStatus.COMPLETED:
            from task_management.tasks import mark_all_subtasks_completed

            mark_all_subtasks_completed.delay(self.id)
