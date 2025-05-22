from django.apps import AppConfig


class TaskManagementConfig(AppConfig):
    """
    Configuration class for the Task Management application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "task_management"

    def ready(self):
        import task_management.signals  # noqa: F401 - Needed to register signal handlers
