from app.models import MainLog
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser


def a_decorator_passing_logs(func):
    def wrapper_logs(request):
        message = {}
        
        try:
            client_address = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            client_address = request.META.get('REMOTE_ADDR')
        
        message['path_info'] = request.META.get('PATH_INFO')
        message['method'] = request.method
        
        user = request.user
        if str(request.user) == 'AnonymousUser':
            user = None
        
        if request.method == 'POST':
            message['post_data'] = request.POST
        
        MainLog(user=user,
                message=message,
                client_address=client_address,
                raw={'raw_message': message,
                     'HTTP_USER_AGENT': request.META.get('HTTP_USER_AGENT'),
                     'HTTP_CONNECTION': request.META.get('HTTP_CONNECTION')}
                ).save()
                # raw=vars(request.META)).save()
        
        return func(request)
    
    return wrapper_logs


def check_recaptcha(function):
    def wrap(request, *args, **kwargs):
        request.recaptcha_is_valid = None
        if request.method == 'POST':
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()
            if result['success']:
                request.recaptcha_is_valid = True
            else:
                request.recaptcha_is_valid = False
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap