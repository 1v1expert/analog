from app.models import MainLog
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
		
		MainLog(user=user, message=message, client_address=client_address, ).save()
		
		return func(request)
	
	return wrapper_logs
