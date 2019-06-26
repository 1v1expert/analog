from django.shortcuts import render, redirect
# from app.forms import ProfileForm

from django.contrib.auth import authenticate, login, logout, models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from catalog.models import DataFile
from catalog import choices
from catalog.handlers import loaded_search_file_handler


from app.forms import MyAuthenticationForm, MyRegistrationForm, AppSearchForm, SearchFromFile
from app.models import MainLog


def a_decorator_passing_logs(message=""):
	def decorator_processing(func):
		def wrapper_logs(request):
			print(vars(request))

			try:
				client_address = request.META['HTTP_X_FORWARDED_FOR']
			except KeyError:
				client_address = request.META.get('REMOTE_ADDR')
	
			MainLog(user=request.user,
			        message=message,
			        client_address=client_address,
			        ).save()
			
			return func(request)
		
		return wrapper_logs
	
	return decorator_processing


def login_view(request):
	auth_form = MyAuthenticationForm(request)
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				MainLog(user=user, message='Авторизация пользователя {} пройдена успешно'.format(username)).save()
				login(request, user)
				return redirect('app:home')
		MainLog(message='Ошибка при авторизации по логин: {}, паролю: {}'.format(username, password)).save()
		return render(request, 'login.html', {'auth_form': auth_form, 'error': 'Неверно введён логин или пароль'})
		# auth = MyAuthenticationForm(request.POST)
		# print(auth.get_user())
	MainLog(message='Страница авторизации').save()
	return render(request, 'login.html', {'auth_form': auth_form})
	# return render(request, 'login.html', {})


@login_required(login_url='/login')
def search(request):
	form = AppSearchForm()
	# form['article'].help_text = 'GG'
	if request.method == 'POST':
		form = AppSearchForm(request.POST)
	MainLog(user=request.user, message='Страница поиска по артикулу').save()
	return render(request, 'search.html', {'user': request.user, 'form': form})
	

@login_required(login_url='/login')
def search_from_file_view(request):
	if request.method == 'POST':
		form = SearchFromFile(request.POST, request.FILES)
		if form.is_valid():
			instance = DataFile(file=request.FILES['file'],
			                    type=choices.TYPES_FILE[1][0],
			                    created_by=request.user,
			                    updated_by=request.user)
			instance.save()
			file_response = loaded_search_file_handler(request.FILES['file'], instance.file, form, request)
			response = HttpResponse(file_response, content_type='text/plain')
			response['Content-Disposition'] = 'attachment; filename=' + file_response.name
			return response
	else:
		form = SearchFromFile()
		MainLog(user=request.user, message='Страница поиска по файлу').save()
		return render(request, 'search_from_file.html', {'user': request.user, 'form': form})


@login_required(login_url='/login')
def advanced_search(request):
	return redirect('catalog:search')


def check_in_view(request):
	reg_form = MyRegistrationForm()
	if request.method == 'POST':
		if request.POST['password'] != request.POST['double_password']:
			return render(request, 'check_in.html', {'reg_form': reg_form, 'error': "Введённые пароли не совпадают"})
		
		user, created = models.User.objects.get_or_create(username=request.POST['username'],
		                                                  defaults={
			                                                  'password': request.POST['password'],
			                                                  'email': request.POST['email']
		                                                  })
		print(user, created)
		if not created:
			return render(request, 'check_in.html', {'reg_form': reg_form, 'error': 'пользователь уже существует'})
		else:
			return render(request, 'check_in.html', {'reg_form': reg_form, 'error': 'пользователь успешно создан'})
		
	try:
		client_address = request.META['HTTP_X_FORWARDED_FOR']
	except KeyError:
		client_address = request.META.get('REMOTE_ADDR')
	
	MainLog(message='Check_in view', client_address=client_address).save()
	return render(request, 'check_in.html', {'reg_form': reg_form})


@login_required(login_url='/login')
@a_decorator_passing_logs(message="Домашняя страница")
def home_view(request):
	return render(request, 'home.html', {'user': request.user})


def logout_view(request):
	MainLog(user=request.user, message='Выход пользователя {} пройдена успешно'.format(request.user)).save()
	logout(request)
	return redirect('app:login')
