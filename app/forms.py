
from app.models import Profile

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


class LoginForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('user',)
