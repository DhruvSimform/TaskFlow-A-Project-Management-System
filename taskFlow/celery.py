import os

from celery import Celery

# Set the default Django settings module for the 'celery' program
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskFlow.settings")

app = Celery("taskFlow")

# Load task modules from all registered Django app configs
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks in installed Django apps
app.autodiscover_tasks()
app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


# app.conf.beat_schedule = {
#     'email-daily-reminder': {
#         'task': 'task_management.tasks.send_task_reminder_emails',
#         'schedule': crontab(hour=11, minute=45),
#     },
# }
