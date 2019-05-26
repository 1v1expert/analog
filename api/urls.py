from django.conf.urls import url
from api.views import get_product
app_name = 'api'
urlpatterns = [
	url(r'^get_product/$', get_product, name='get_product')
]
