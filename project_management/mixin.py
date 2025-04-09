from django.db import models

from account.models import CustomUser


class DataTimeMixIn(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CreatedUpdatedByMixin(models.Model):
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.DO_NOTHING, related_name="projects_created"
    )
    updated_by = models.ForeignKey(
        CustomUser, on_delete=models.DO_NOTHING, related_name="projects_updated"
    )

    class Meta:
        abstract = True


# class SoftDeletedMixIn(models.Model):
#     is_soft
