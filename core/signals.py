from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Schedule


@receiver(post_save, sender=Schedule)
def appointment_confirmed_email(sender, instance, created, **kwargs):
    if created:
        return
    
    old_status = Schedule.objects.get(pk=instance.pk).status

    if old_status != "confirmed" and instance.status == "confirmed":
        send_confirmation_email(instance)


def send_confirmation_email(appointment: Schedule):
    user = appointment.booked_by
    if not user or not user.email:
        return
    
    context = {
        "user": user,
        "appointment": appointment,
    }

    subject = "Ваша запись подтверждена"

    html_content = render_to_string("emails/appointment_confirmed.html", context)

    text_content = render_to_string("emails/appointment_confirmed.txt", context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()