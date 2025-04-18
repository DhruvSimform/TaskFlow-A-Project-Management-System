from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from task_management.tasks import (
    check_and_complete_parent_task,
    mark_all_subtasks_completed,
)

from .models import Task, TaskCollaborator, TaskStatus


class SubTaskInline(admin.TabularInline):
    """
    Inline admin interface for managing subtasks of a parent task.
    """

    model = Task
    fk_name = "parent_task"
    extra = 0
    show_change_link = True
    fields = ("title", "status", "priority", "start_date", "due_date")


class TaskCollabratorInline(admin.TabularInline):
    """
    Inline admin class for managing TaskCollaborator instances within the Task model in the Django admin interface.
    """

    model = TaskCollaborator
    extra = 1
    autocomplete_fields = ["user"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing Task objects with custom display, filters, and background task triggers.
    """

    list_display = (
        "title",
        "colored_status",
        "priority",
        "start_date",
        "due_date",
        "completed_date",
        "created_by",
        "updated_by",
        "is_overdue",
        "collaborator_count",
    )
    list_filter = ("status", "priority", "start_date", "due_date", "completed_date")
    search_fields = ("title", "description", "created_by__email", "updated_by__email")
    readonly_fields = ("start_date", "completed_date", "created_by", "updated_by")
    ordering = ("-start_date",)
    date_hierarchy = "start_date"
    inlines = [SubTaskInline, TaskCollabratorInline]

    def colored_status(self, obj):
        color_map = {
            "P": "gray",
            "I": "blue",
            "C": "green",
            "O": "red",
            "H": "orange",
        }
        return format_html(
            '<span style="color:{};"><strong>{}</strong></span>',
            color_map.get(obj.status, "black"),
            obj.get_status_display(),
        )

    colored_status.short_description = "Status"

    def is_overdue(self, obj):
        if obj.due_date and obj.status not in ["C", "H"]:
            return obj.due_date < timezone.now()
        return False

    is_overdue.boolean = True
    is_overdue.short_description = "Overdue?"

    def collaborator_count(self, obj):
        return obj.collaborators.count()

    collaborator_count.short_description = "Collaborators"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("created_by", "updated_by")
            .prefetch_related("collaborators", "sub_tasks")
        )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
        # Trigger background tasks after saving the model
        if obj.parent_task_id:
            check_and_complete_parent_task.delay(obj.id)

        if obj.status == TaskStatus.COMPLETED:
            mark_all_subtasks_completed.delay(obj.id)


@admin.register(TaskCollaborator)
class TaskCollaboratorAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing TaskCollaborator model in the Django admin interface.
    """

    list_display = ("user", "task", "added_by", "added_at")
    search_fields = ("user__email", "task__title", "added_by__email")
    readonly_fields = ("added_at",)
