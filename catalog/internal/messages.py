from django.conf import settings
from django.core.mail import get_connection, send_mail


def send_email(header, body, to):
    connection = get_connection(host=settings.EMAIL_HOST, port=settings.EMAIL_PORT,
                                username=settings.EMAIL_HOST_USER,
                                password=settings.EMAIL_HOST_PASSWORD, use_tls=settings.EMAIL_USE_TLS)
    send_mail(header, body, to, connection=connection, fail_silently=False)