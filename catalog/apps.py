from django.apps import AppConfig
from django.contrib.auth.apps import AuthConfig


class CatalogConfig(AppConfig):
    name = 'catalog'
    verbose_name="Функционал прикладного администратора"

class AnalogAuthConfig(AuthConfig):
    verbose_name = "Функционал системного администратора"