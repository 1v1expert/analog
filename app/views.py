from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate, login, logout, models, forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.mail import get_connection, send_mail
from django.conf import settings

from catalog.models import DataFile
from catalog import choices
from catalog.handlers import loaded_search_file_handler


from app.forms import MyAuthenticationForm, MyRegistrationForm, AppSearchForm, SearchFromFile, EmailConfirmationForm
from app.decorators import a_decorator_passing_logs

import hashlib


@a_decorator_passing_logs
def login_view(request):
	auth_form = MyAuthenticationForm(request)
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		print(user)
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
	# reg_form = forms.UserCreationForm()
	if request.method == 'POST':
		if request.POST['password'] != request.POST['double_password']:
			return render(request, 'check_in.html', {'reg_form': reg_form, 'error': "Введённые пароли не совпадают"})
		if len(request.POST['password']) < 8:
			return render(request, 'check_in.html', {'reg_form': reg_form, 'error': "Введённый пароль слишком короткий. Он должен содержать как минимум 8 символов. "})
		
		user, created = models.User.objects.get_or_create(username=request.POST['username'],
		                                                  defaults={
			                                                  # 'password': request.POST['password'],
			                                                  'email': request.POST['email'],
			                                                  'is_active': False
		                                                  })
		if not created:
			return render(request, 'check_in.html', {'reg_form': reg_form, 'error': 'пользователь уже существует'})
		else:
			if not user.check_password(request.POST['password']):
				user.delete()
				return render(request, 'check_in.html', {'reg_form': reg_form, 'error': 'Введённый пароль состоит только из цифр, некорректен.'})
			user.set_password(request.POST['password'])
			user.save()
			try:
				connection = get_connection(host=settings.EMAIL_HOST, port=settings.EMAIL_PORT, username=settings.EMAIL_HOST_USER,
				                            password=settings.EMAIL_HOST_PASSWORD, use_tls=settings.EMAIL_USE_TLS)
				verif_code = hashlib.md5('{}'.format(user.pk).encode()).hexdigest()
				href = 'http://analogpro.ru/email_confirmation/{}-{}/'.format(verif_code, user.pk)
				send_mail('Подтверждение почты',
				          'Ваш верификационный код - {}, введите его или перейдите по ссылке: {}\n'.format(verif_code,
				                                                                                         href),
				          'info@analogpro.ru', [request.POST['email']], connection=connection, fail_silently=False)
				# print(response_email, [request.POST['email']])
			except:
				return render(request, 'check_in.html', {'reg_form': reg_form, 'error': 'Произошла проблема при отправке email'})
			# return render(request, 'check_in.html', {'reg_form': reg_form, 'error': 'пользователь успешно создан'})
			return redirect('app:email_confirmation', user.pk, user.pk)
		
	return render(request, 'check_in.html', {'reg_form': reg_form})


@login_required(login_url='/login')
@a_decorator_passing_logs
def home_view(request):
	return render(request, 'home.html', {'user': request.user})


@login_required(login_url='/login')
@a_decorator_passing_logs
def faq_view(request):
	return render(request, 'faq.html', {'user': request.user})


@login_required(login_url='/login')
@a_decorator_passing_logs
def partners_view(request):
	return render(request, 'to_partners.html', {'user': request.user})


@login_required(login_url='/login')
@a_decorator_passing_logs
def contacts_view(request):
	return render(request, 'contacts.html', {'user': request.user})


@a_decorator_passing_logs
def logout_view(request):
	logout(request)
	return redirect('app:login')


def email_confirmation(request, verification_code, user_id):
	user = get_object_or_404(models.User, pk=user_id)
	check_code = hashlib.md5('{}'.format(user.pk).encode()).hexdigest()
	msg = 'Подтвердите email'
	if verification_code == check_code:
		user.is_active = True
		user.save()
		msg = 'E-mail подтверждён'
		return render(request, 'email_confirmation.html', {'confirmation': True, 'user': user, 'msg': msg})
	
	elif verification_code == user_id:
		confirmation_form = EmailConfirmationForm()
		if request.method == 'POST':
			confirmation_form = EmailConfirmationForm(request)
			if check_code == request.POST['code']:
				user.is_active = True
				user.save()
				msg = 'E-mail подтверждён'
				return render(request, 'email_confirmation.html',
				              {'confirmation': True, 'user': user, 'msg': msg})
			else:
				msg = 'Код неверен'
		return render(request, 'email_confirmation.html', {'conf_form': confirmation_form, 'user': user, 'msg': msg})
