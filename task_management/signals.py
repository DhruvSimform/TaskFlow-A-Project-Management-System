# task_management/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TaskCollaborator
from .tasks import send_task_collaborator_email_celery


@receiver(post_save, sender=TaskCollaborator)
def notify_collaborator(sender, instance, created, **kwargs):
    """
    Sends an email notification to a task collaborator when a new collaborator is added.
    """

    if created:
        send_task_collaborator_email_celery.delay(
            task_id=instance.task.id,
            user_id=instance.user.id,
            added_by_id=(
                instance.added_by.id
                if instance.added_by
                else instance.task.created_by.id
            ),
        )
