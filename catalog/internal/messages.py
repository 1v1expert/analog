from django.conf import settings
from django.core.mail import get_connection, send_mail


def send_email_with_connection(header, body, to):
    connection = _get_connection()
    send_mail(header, body, 'info@analogpro.ru', to, connection=connection, fail_silently=False)


def _get_connection():
    return get_connection(host=settings.EMAIL_HOST, port=settings.EMAIL_PORT,
                          username=settings.EMAIL_HOST_USER,
                          password=settings.EMAIL_HOST_PASSWORD, use_tls=settings.EMAIL_USE_TLS)
