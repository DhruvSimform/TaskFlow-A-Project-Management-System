from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from account.models import CustomUser
from task_management.models import Task, TaskCollaborator, TaskPriority, TaskStatus


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


@shared_task
def send_task_collaborator_email_celery(task_id, user_id, added_by_id):
    try:
        task = Task.objects.get(pk=task_id)
        user = CustomUser.objects.get(pk=user_id)
        added_by = CustomUser.objects.get(pk=added_by_id)

        subject = f"[TaskFlow] You've been added as a collaborator to: {task.title}"
        from_email = settings.DEFAULT_FROM_EMAIL
        # to_email = [user.email]
        to_email = ["pateldhruvn2004@gmail.com", user.email]

        context = {
            "user_name": user.name,
            "project_name": task.project.name,
            "project_description": task.project.description,
            "added_by": added_by.name,
            "task_title": task.title,
            "task_description": task.description,
            "start_date": task.start_date.strftime("%b %d, %Y %I:%M %p"),
            "due_date": (
                task.due_date.strftime("%b %d, %Y %I:%M %p") if task.due_date else "N/A"
            ),
            "priority": task.get_priority_display(),
        }

        html_content = render_to_string("emails/task_assigned.html", context)

        msg = EmailMultiAlternatives(subject, "", from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    except (Task.DoesNotExist, CustomUser.DoesNotExist) as e:
        print(str(e))

        pass


PRIORITY_ORDER = {
    TaskPriority.HIGH: 1,
    TaskPriority.MEDIUM: 2,
    TaskPriority.LOW: 3,
}


@shared_task
def send_task_reminder_emails():
    user_ids = TaskCollaborator.objects.values_list("user", flat=True).distinct()
    for user_id in user_ids:
        send_single_task_reminder_email.delay(user_id)  # Trigger in parallel


@shared_task
def send_single_task_reminder_email(user_id):
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.utils import timezone

    try:
        user = CustomUser.objects.get(id=user_id)

        user_tasks = (
            Task.objects.filter(
                collaborators__id=user_id,
                status__in=[
                    TaskStatus.PENDING,
                    TaskStatus.IN_PROGRESS,
                    TaskStatus.OVERDUE,
                ],
            )
            .prefetch_related("project")
            .order_by("priority", "due_date")
        )

        if not user_tasks.exists():
            return

        PRIORITY_ORDER = {
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
        }

        # Group tasks by project
        project_task_map = {}
        for task in user_tasks:
            project_name = task.project.name
            if project_name not in project_task_map:
                project_task_map[project_name] = []

            project_task_map[project_name].append(task)

        # Sort tasks by priority and due date
        for project_name, tasks in project_task_map.items():
            tasks.sort(
                key=lambda t: (
                    PRIORITY_ORDER.get(t.priority, float("inf")),
                    t.due_date or timezone.now(),
                )
            )

        context = {
            "user": user,
            "project_task_map": project_task_map,
            "today": timezone.now().date(),
        }

        subject = "⏰ Daily Task Reminder - TaskFlow"
        from_email = "noreply@taskflow.com"
        to_email = "pateldhruvn2004@gmail.com"  # Replace with test email if needed

        text_body = render_to_string("emails/task_reminder.txt", context)
        html_body = render_to_string("emails/task_reminder.html", context)

        email = EmailMultiAlternatives(subject, text_body, from_email, [to_email])
        email.attach_alternative(html_body, "text/html")
        email.send()

    except CustomUser.DoesNotExist:
        return
