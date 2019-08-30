from django.conf.urls import url
from django.contrib import admin
from app_2.views import redirect_to_old_template, view_main_page
app_name = 'app_2'
urlpatterns = [
	# url(r'^login/$', login_view, name='login'),
	# url(r'^check_in/$', check_in_view, name='check_in'),
	# url(r'^search/$', search, name='search'),
	# # url(r'^search/$', search, name='search_from_file'),
	# url(r'^search_from_file/$', search_from_file_view, name='search_from_file'),
	# url(r'^contacts', contacts_view, name='contacts_page'),
	# url(r'^partners', partners_view, name='partners_page'),
	# url(r'^profile/', profile_view, name='profile_page'),
	# url(r'^faq', faq_view, name='faq_page'),
	# url(r'^advanced_search/$', search, name='advanced_search'),
	# url(r'^logout/$', logout_view, name='logout'),
	# url(r'^email_confirmation/(?P<verification_code>[0-9\w-]+)-(?P<user_id>[0-9]+)/$',
	#     email_confirmation, name='email_confirmation'),
	url(r'^home/$', view_main_page, name='new_home'),
	url(r'^$', view_main_page, name='redirect_to_old_template'),
	# url(r'^admin/', admin.site.urls),
]
