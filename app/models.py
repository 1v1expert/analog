from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres import fields as pgfields
from django.utils import timezone
from django.utils.translation import gettext, gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
# from django.contrib.admin.models import LogEntry


AUTHORIZATION = 1
SEARCH = 2
LOGOUT = 3
COMMON = 4

ACTION_FLAG_CHOICES = (
    (AUTHORIZATION, _('Авторизация')),
    (SEARCH, _('Поиск')),
    (LOGOUT, _('Выход из системы')),
    (COMMON, _('Общий'))
)


class FeedBack(models.Model):
    action_time = models.DateTimeField(_('action time'), default=timezone.now, editable=False, )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, blank=True, null=True, verbose_name=_('user'), )
    name = models.TextField(max_length=50, blank=True, null=True, verbose_name="Имя")
    email = models.TextField(max_length=100, blank=True, null=True, verbose_name="Почта")
    phone = models.TextField(max_length=40, blank=True, null=True, verbose_name="Телефон")
    text = models.TextField(max_length=500, blank=True, null=True, verbose_name="Текст")
    is_subscriber = models.BooleanField(default=False, null=True, verbose_name="Подписка")
    
    class Meta:
        verbose_name = "Обратная связь"
        verbose_name_plural = "Обратная связь"
        ordering = ('-action_time',)
    

class MainLog(models.Model):
    action_time = models.DateTimeField(_('action time'), default=timezone.now, editable=False, )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, blank=True, null=True, verbose_name=_('user'),)
    client_address = models.TextField(max_length=100, blank=True, null=True, verbose_name="Адрес клиента")
    message = models.TextField(_('message'), blank=True)
    raw = pgfields.JSONField(null=True, blank=True, verbose_name="Голые данные")
    has_errors = models.BooleanField(default=False, null=True)
    # action_flag = models.PositiveSmallIntegerField(_('action flag'), choices=ACTION_FLAG_CHOICES)
    
    class Meta:
        verbose_name = "Лог активности"
        verbose_name_plural = "Логи активности"
        ordering = ('-action_time',)
    
    def __str__(self):
        return '{}; {}'.format(self.user, self.message)
        

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, verbose_name="Расширенные данные")
    token = models.UUIDField(default=uuid.uuid4, verbose_name="Авторизационный токен")
    
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
    
    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name
    
# todo: this code maybe need in the future, need rewrite
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Client.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
