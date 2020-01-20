from django.conf.urls import url
from api.views import check_product_and_get_attributes, search_from_form, advanced_search, \
    feedback, logout_view, login_view, registration_view, subscriber, search_article, report_an_error

app_name = 'api'
urlpatterns = [
    url(r'^get_product/$', check_product_and_get_attributes, name='get_product'),
    url(r'^search/$', search_from_form, name='search'),
    url(r'^advanced_search/$', advanced_search, name='advanced_search'),
    url(r'^feedback/$', feedback, name='feedback'),
    url(r'^subscriber/$', subscriber, name='subscriber'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^login/$', login_view, name='login'),
    url(r'^register/$', registration_view, name='registration'),
    url(r'^search_article/$', search_article, name='search_article'),
    url(r'^report_an_error/$', report_an_error, name='report_an_error')
    # url(r'^old/email_confirmation/(?P<verification_code>[0-9\w-]+)-(?P<user_id>[0-9]+)/$',
]
