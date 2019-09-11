from django.conf.urls import url
from django.contrib import admin
from app.views import login_view, check_in_view, home_view, logout_view, search, search_from_file_view, email_confirmation, faq_view, contacts_view, partners_view, profile_view, landing_page_view
app_name = 'app'
urlpatterns = [
	url(r'^old/login/$', login_view, name='login'),
	url(r'^old/check_in/$', check_in_view, name='check_in'),
	url(r'^old/search/$', search, name='search'),
	# url(r'^search/$', search, name='search_from_file'),
	url(r'^old/search_from_file/$', search_from_file_view, name='search_from_file'),
	url(r'^old/contacts', contacts_view, name='contacts_page'),
	url(r'^old/partners', partners_view, name='partners_page'),
	url(r'^old/profile/', profile_view, name='profile_page'),
	url(r'^old/faq', faq_view, name='faq_page'),
	url(r'^old/advanced_search/$', search, name='advanced_search'),
	url(r'^old/logout/$', logout_view, name='logout'),
	url(r'^old/email_confirmation/(?P<verification_code>[0-9\w-]+)-(?P<user_id>[0-9]+)/$',
	    email_confirmation, name='email_confirmation'),
	url(r'^old/', home_view, name='home'),
	url(r'^$', landing_page_view, name='landing_home')
	# url(r'^admin/', admin.site.urls),
]
