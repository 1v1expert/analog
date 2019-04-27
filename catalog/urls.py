from django.conf.urls import url
from catalog.views import search_view, advanced_search_view, search_from_file_view
app_name = 'catalog'
urlpatterns = [
	#url(r'^index', views.render_page),
	url(r'^$', search_view, name='search'),
	url(r'^advanced/(?P<product_id>[0-9]+)-(?P<manufacturer_to>[0-9]+)/$', advanced_search_view, name='advanced_search'),
	url(r'^from_file/$', search_from_file_view, name='search_from_file')
]
