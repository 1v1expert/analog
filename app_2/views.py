from django.shortcuts import redirect, render
from app_2.forms import SearchForm


def redirect_to_old_template(request):
	return redirect('app:home')


def view_main_page(request):
	form = SearchForm()
	from django.conf import settings
	print(settings.TEMPLATES)
	return render(request, 'main.html', {'form': form})

# https://ianlunn.github.io/Hover/
