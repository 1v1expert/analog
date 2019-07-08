from django.conf.urls import url
from django.contrib import admin
from app.views import login_view, check_in_view, home_view, logout_view, search, search_from_file_view, email_confirmation
app_name = 'app'
urlpatterns = [
	url(r'^login/$', login_view, name='login'),
	url(r'^check_in/$', check_in_view, name='check_in'),
	url(r'^search/$', search, name='search'),
	url(r'^search_from_file/$', search_from_file_view, name='search_from_file'),
	url(r'^advanced_search/$', search, name='advanced_search'),
	url(r'^logout/$', logout_view, name='logout'),
	url(r'^email_confirmation/(?P<verification_code>[0-9\w-]+)-(?P<user_id>[0-9]+)/$', email_confirmation, name='email_confirmation'),
	url(r'^$', home_view, name='home'),
	# url(r'^admin/', admin.site.urls),
]
