"""
Конфигурации корневаого роутинга

Подробная информация: https://docs.djangoproject.com/en/2.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

admin.site.site_header = "Система Analog"
admin.site.site_title = "Система Analog"
admin.site.index_title = "Система Analog"

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),
    path('', admin.site.urls),
]