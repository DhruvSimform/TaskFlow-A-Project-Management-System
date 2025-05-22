from django.contrib import admin

from .models import Project, ProjectCollaborator


class ProjectCollaboratorInline(admin.TabularInline):
    """
    Inline admin class for managing ProjectCollaborator instances within the Project admin interface.
    """

    model = ProjectCollaborator
    extra = 1
    autocomplete_fields = ["user"]
    readonly_fields = ["addeed_at"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing Project model in the Django admin interface.
    """

    list_display = ("name", "status", "created_by", "updated_by", "is_deleted")
    search_fields = ("name", "description")
    readonly_fields = ("created_by", "updated_by")
    fields = ("name", "description", "status", "created_by", "updated_by")
    inlines = [ProjectCollaboratorInline]

    def save_model(self, request, obj, form, change):
        # If it's a new object, set `created_by` and `updated_by`
        if not change:  # The object is being created (not updated)
            obj.created_by = request.user

        # Always update `updated_by` when saving
        obj.updated_by = request.user

        # Call the parent save_model to save the object
        super().save_model(request, obj, form, change)
