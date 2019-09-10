from django import forms
from catalog.models import Manufacturer


class SearchForm(forms.Form):
	article = forms.CharField(widget=forms.TextInput(attrs={'class': 'search',
	                                                        'placeholder': "Введите номер артикула",
	                                                        'data-toggle': 'dropdown'
	                                                        }))
	manufacturer_to = forms.ModelChoiceField(queryset=Manufacturer.objects.all(), widget=forms.Select(), empty_label=None)