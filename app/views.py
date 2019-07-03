from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout, models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from catalog.models import DataFile
from catalog import choices
from catalog.handlers import loaded_search_file_handler


from app.forms import MyAuthenticationForm, MyRegistrationForm, AppSearchForm, SearchFromFile
from app.decorators import a_decorator_passing_logs


@a_decorator_passing_logs
def login_view(request):
	auth_form = MyAuthenticationForm(request)
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect('app:home')
		return render(request, 'login.html', {'auth_form': auth_form, 'error': 'Неверно введён логин или пароль'})

	return render(request, 'login.html', {'auth_form': auth_form})


@a_decorator_passing_logs
@login_required(login_url='/login')
def search(request):
	form = AppSearchForm()

	if request.method == 'POST':
		form = AppSearchForm(request.POST)
		
	return render(request, 'search.html', {'user': request.user, 'form': form})
	

@a_decorator_passing_logs
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
		return render(request, 'search_from_file.html', {'user': request.user, 'form': form})


@a_decorator_passing_logs
@login_required(login_url='/login')
def advanced_search(request):
	return redirect('catalog:search')


@a_decorator_passing_logs
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

		if not created:
			return render(request, 'check_in.html', {'reg_form': reg_form, 'error': 'пользователь уже существует'})
		else:
			from django.core.mail import send_mail
			import hashlib
			verif_code = hashlib.md5('{}'.format(user.pk).encode()).hexdigest()
			send_mail('Подтверждение почты',
			          'Ваш верификационный код - {}'.format(verif_code),
			          [request.POST['email']],
			          fail_silently=False)
			return render(request, 'check_in.html', {'reg_form': reg_form, 'error': 'пользователь успешно создан'})
		
	return render(request, 'check_in.html', {'reg_form': reg_form})


@login_required(login_url='/login')
@a_decorator_passing_logs
def home_view(request):
	return render(request, 'home.html', {'user': request.user})


@a_decorator_passing_logs
def logout_view(request):
	logout(request)
	return redirect('app:login')
