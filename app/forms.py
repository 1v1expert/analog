
from app.models import Profile
from catalog.models import Manufacturer

from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django import forms
from django.utils.translation import gettext_lazy as _


class MyAuthenticationForm(AuthenticationForm):
	username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True,
	                                                       'class': 'form-control',
	                                                       'placeholder': "Введите имя пользователя"
	                                                       }))
	password = forms.CharField(label=_("Password"), strip=False, widget=forms.PasswordInput(attrs={
		'class': 'form-control', 'placeholder': "Введите пароль"
	}), )


class AppSearchForm(forms.Form):
	article = forms.CharField(label='Артикул', widget=forms.TextInput(attrs={'autofocus': True,
	                                                                         'class': 'form-control',
	                                                                         'placeholder': "Введите артикул товара"
	                                                                         }))
	manufacturer_from = forms.ModelChoiceField(label='Исходный производитель', empty_label=None,
	                                           queryset=Manufacturer.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
	manufacturer_to = forms.ModelChoiceField(label='Необходимый производитель', empty_label=None,
	                                         queryset=Manufacturer.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))


class LoginForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('user',)
