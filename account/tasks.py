from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@shared_task
def send_password_reset_email(email, reset_link):
    subject = "Reset Your Password - TaskFlow"
    from_email = "no-reply@taskflow.com"
    to_email = ["pateldhruvn2004@gmail.com"]

    html_content = render_to_string(
        "emails/password_reset.html",
        {
            "reset_link": reset_link,
        },
    )
    text_content = f"Click the link to reset your password: {reset_link}"

    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
