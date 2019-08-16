from django.shortcuts import redirect, render


def redirect_to_old_template(request):
	return redirect('app:home')


def view_main_page(request):
	return render(request, 'index.html', {})
