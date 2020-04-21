from django.conf.urls import url
from django.contrib import admin
from app.views import search_from_file_view, landing_page_view, landing_confirm_mail_page

app_name = 'app'
urlpatterns = [
    url(r'^old/search_from_file/$', search_from_file_view, name='search_from_file'),
    url(r'^email_confirmation/(?P<verification_code>[0-9\w-]+)-(?P<user_id>[0-9]+)/$',
        landing_confirm_mail_page, name='email_confirmation'),
    url(r'^(?P<lang>[a-z]{2})/$', landing_page_view, name='landing_home'),
    url(r'^$', landing_page_view, name='landing_home')
]
