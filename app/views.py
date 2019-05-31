from django.shortcuts import render, redirect
# from app.forms import ProfileForm

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from catalog.models import DataFile
from catalog import choices
from catalog.handlers import loaded_search_file_handler

from app.forms import MyAuthenticationForm, AppSearchForm, SearchFromFile


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
		# auth = MyAuthenticationForm(request.POST)
		# print(auth.get_user())
	return render(request, 'login.html', {'auth_form': auth_form})
	# return render(request, 'login.html', {})


@login_required(login_url='/login')
def search(request):
	form = AppSearchForm()
	# form['article'].help_text = 'GG'
	if request.method == 'POST':
		form = AppSearchForm(request.POST)
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
		return render(request, 'search_from_file.html', {'user': request.user, 'form': form})


@login_required(login_url='/login')
def advanced_search(request):
	return redirect('catalog:search')


def check_in_view(request):
	client_form = ProfileForm(request.user.profile)
	return render(request, 'check_in.html', {
		'client_form': client_form
	})


@login_required(login_url='/login')
def home_view(request):
	return render(request, 'home.html', {'user': request.user})


def logout_view(request):
	logout(request)
	return redirect('app:login')
