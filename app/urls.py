from django.conf.urls import url
from django.contrib import admin
from app.views import login_view, check_in_view, home_view, logout_view, search
app_name = 'app'
urlpatterns = [
	url(r'^login/$', login_view, name='login'),
	url(r'^check_in/$', check_in_view, name='check_in'),
	url(r'^search/$', search, name='search'),
	url(r'^logout/$', logout_view, name='logout'),
	url(r'^$', home_view, name='home'),
	# url(r'^admin/', admin.site.urls),
]
