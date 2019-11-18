# -*- coding: utf-8 -*-

from django.db.models import signals  # NOQA
from django.dispatch import receiver
from smtplib import SMTPDataError
from app.models import FeedBack

from catalog.internal.messages import send_email_with_connection


@receiver(signals.post_save, sender=FeedBack)
def register_transaction(sender, instance, *args, **kwargs):
    message = ''
    if instance.is_subscriber:
        message += 'На сайте оформлена подписка на рассылку по адресу: {}, пользователем {}'.format(
            instance.email, instance.user)
    else:
        message += 'На сайте оставлено сообщение.\n'
        message += 'Phone: {}\nName: {}\nE-mail: {}\nText: {}\nUser: {}'.format(
            instance.phone,
            instance.name,
            instance.email,
            instance.text,
            instance.user
        )
    
    try:
        send_email_with_connection('Msg from AnalogPro, time: {}'.format(instance.action_time.strftime('%Y:%m:%d %H:%M')),
                                   message,
                                   ['mojaev-a@yandex.ru'])
    except SMTPDataError as e:
        print(e)
#SMTPDataError: