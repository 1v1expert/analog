from django.conf.urls import url
from app.views import login_view
app_name = 'app'
urlpatterns = [
	url(r'^login/$', login_view, name='login')
]
