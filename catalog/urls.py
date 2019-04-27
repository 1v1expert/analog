from django.conf.urls import url
from catalog.views import search_view, advanced_search_view
app_name = 'catalog'
urlpatterns = [
	#url(r'^index', views.render_page),
	url(r'^$', search_view, name='search'),
	url(r'^advanced/(?P<product_id>[0-9]+)/$', advanced_search_view, name='advanced_search'),
]
