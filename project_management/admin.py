from django.contrib import admin

from .models import Project, ProjectCollaborator


class ProjectCollaboratorInline(admin.TabularInline):
    model = ProjectCollaborator
    extra = 1
    autocomplete_fields = [
        "user"
    ]  # Optional: makes user selection easier if many users
    readonly_fields = ["addeed_at"]  # You can remove this if you want to edit it


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
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
