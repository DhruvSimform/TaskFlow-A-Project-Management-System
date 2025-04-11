from celery import shared_task
from django.utils import timezone

from task_management.models import Task, TaskStatus


@shared_task
def check_and_complete_parent_task(task_id):
    try:
        task = Task.objects.select_related("parent_task").get(id=task_id)
    except Task.DoesNotExist:
        return

    parent = task.parent_task
    if not parent:
        return

    sibling_statuses = parent.sub_tasks.values_list("status", flat=True)

    if all(status == TaskStatus.COMPLETED for status in sibling_statuses):
        if parent.status != TaskStatus.COMPLETED:
            parent.status = TaskStatus.COMPLETED
            parent.completed_date = timezone.now()
            parent.save(update_fields=["status", "completed_date"])
    else:
        if parent.status == TaskStatus.COMPLETED:
            parent.status = TaskStatus.IN_PROGRESS
            parent.completed_date = None
            parent.save(update_fields=["status", "completed_date"])

    # ✅ Always recurse no matter what
    check_and_complete_parent_task.delay(parent.id)


@shared_task
def mark_all_subtasks_completed(task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return

    subtasks = task.sub_tasks.exclude(status=TaskStatus.COMPLETED)
    for sub in subtasks:
        sub.status = TaskStatus.COMPLETED
        sub.completed_date = timezone.now()
        sub.save(update_fields=["status", "completed_date"])
        mark_all_subtasks_completed.delay(sub.id)  # 🔁 async recursion
