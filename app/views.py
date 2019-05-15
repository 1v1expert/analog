from django.shortcuts import render


def login_view(request):
	return render(request, 'login.html', {})


def check_in_view(request):
	return render(request, 'check_in.html', {})
