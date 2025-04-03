from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@shared_task
def send_welcome_email(email, first_name, password):
    """Send a welcome email when an admin creates a new user."""

    subject = "Welcome to TaskFlow - Your Account Details"

    # Render the HTML email template
    html_content = render_to_string(
        "emails/welcome_email.html",
        {
            "first_name": first_name,
            "email": email,
            "password": password,
        },
    )

    # Create email message with HTML content
    email_msg = EmailMultiAlternatives(subject, "", settings.EMAIL_HOST_USER, [email])
    email_msg.attach_alternative(html_content, "text/html")

    try:
        email_msg.send()
        return f"Welcome email sent to {email}"
    except Exception as e:
        from account.models import CustomUser

        CustomUser.objects.filter(email=email).delete()  # Delete user if email fails
        return f"Failed to send email to {email}: {str(e)}"
