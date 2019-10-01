from django.conf.urls import url
from api.views import check_product_and_get_attributes, search_from_form, advanced_search, \
    feedback, logout_view, login_view

app_name = 'api'
urlpatterns = [
    url(r'^get_product/$', check_product_and_get_attributes, name='get_product'),
    url(r'^search/$', search_from_form, name='search'),
    url(r'^advanced_search/$', advanced_search, name='advanced_search'),
    url(r'^feedback/$', feedback, name='feedback'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^old/login/$', login_view, name='login'),
]
