"""
Конфигурации корневаого роутинга

Подробная информация: https://docs.djangoproject.com/en/2.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
import app
from catalog.views import search_view

admin.site.site_header = "Система Analog"
admin.site.site_title = "Система Analog"
admin.site.index_title = "Система Analog"

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^admin/search/', include('catalog.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^', include('app.urls')),
    # url(r'^old/', include('app.urls')),
    url(r'^admin/', admin.site.urls),
    
] + static(settings.FILES_URL, document_root=settings.FILES_ROOT)
