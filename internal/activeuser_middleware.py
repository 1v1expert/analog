import datetime
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class ActiveUserMiddleware(MiddlewareMixin):
    
    @staticmethod
    def process_request(request):
        current_user = request.user
        if request.user.is_authenticated():
            now = datetime.datetime.now()
            cache.set('seen_%s' % (current_user.username), now, settings.USER_LASTSEEN_TIMEOUT)
            
# for read http://www.djangocurrent.com/2011/07/django-using-cashing-to-track-online.html
# https://stackoverflow.com/questions/29663777/how-to-check-whether-a-user-is-online-in-django-template
