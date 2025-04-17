from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@shared_task
def send_collaborator_email(user_email, context):
    """Send email to notify user of being added as a project collaborator."""

    subject = f"You've been added to project '{context['project_name']}' in TaskFlow"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user_email]
    cc_email = ["pateldhruvn2004@gmail.com"]

    # Render HTML and plain text version
    html_content = render_to_string("emails/add_collaborator.html", context)
    text_content = f"Hi {context['user_name']},\n\nYou’ve been added to the project '{context['project_name']}' on TaskFlow.\n\nRegards,\nTaskFlow Team"

    msg = EmailMultiAlternatives(
        subject, text_content, from_email, to=to_email, cc=cc_email
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
