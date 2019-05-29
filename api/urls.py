from django.conf.urls import url
from api.views import get_product, search, advanced_search
app_name = 'api'
urlpatterns = [
	url(r'^get_product/$', get_product, name='get_product'),
	url(r'^search/$', search, name='search'),
	url(r'^advanced_search/$', advanced_search, name='advanced_search'),
]
