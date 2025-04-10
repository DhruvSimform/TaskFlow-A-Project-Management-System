from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Project, ProjectCollaborator


@receiver(post_save, sender=Project)
def add_project_owner_in_collaborator(sender, instance, created, **kwargs):
    if created:
        collaborator = ProjectCollaborator.objects.create(
            project=instance, user=instance.created_by, added_by=instance.created_by
        )
        collaborator.save()
