from django.conf.urls import url
from app.views import login_view, check_in_view
app_name = 'app'
urlpatterns = [
	url(r'^login/$', login_view, name='login'),
	url(r'^check_in/$', check_in_view, name='check_in')
]
