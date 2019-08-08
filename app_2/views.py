from django.shortcuts import redirect


def redirect_to_old_template(request):
	return redirect('app:home')