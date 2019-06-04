from django.conf.urls import url
from api.views import check_product_and_get_attributes, search, advanced_search
app_name = 'api'
urlpatterns = [
	url(r'^get_product/$', check_product_and_get_attributes, name='get_product'),
	url(r'^search/$', search, name='search'),
	url(r'^advanced_search/$', advanced_search, name='advanced_search'),
]
