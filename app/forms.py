from app.models import Profile
from catalog.models import Manufacturer

from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django import forms
from django.utils.translation import gettext_lazy as _


class EmailConfirmationForm(forms.Form):
    code = forms.CharField(label="Код подтверждения", strip=False,
                           widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control',
                                                         'placeholder': "Введите код подтверждения"
                                                         }
                                                  )
                           )


class MyAuthenticationForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True,
                                                           'class': 'form-control',
                                                           'placeholder': "Введите имя пользователя"
                                                           }))
    password = forms.CharField(label=_("Password"), strip=False, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': "Введите пароль"
    }), )


class MyRegistrationForm(forms.Form):
    username = forms.CharField(label=_('Логин'), widget=forms.TextInput(attrs={'autofocus': True,
                                                                               'class': 'form-control',
                                                                               'placeholder': "Введите имя пользователя"
                                                                               }))
    password = forms.CharField(label="Пароль", strip=False, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': "Введите пароль"}), )
    double_password = forms.CharField(label="Подтверждение пароля", strip=False, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': "Повторите пароль"}), )
    email = forms.EmailField(label=_("E-mail"), widget=forms.EmailInput(attrs={'autofocus': True, 'type': 'email',
                                                                               'class': 'form-control',
                                                                               'placeholder': "Введите email"
                                                                               }))


class SearchFromFile(forms.Form):
    file = forms.FileField(label='Файл', required=False,
                           widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    manufacturer_from = forms.ModelChoiceField(label='Исходный производитель', empty_label=None,
                                               queryset=Manufacturer.objects.all(),
                                               widget=forms.Select(attrs={'class': 'form-control'}))
    manufacturer_to = forms.ModelChoiceField(label='Необходимый производитель', empty_label=None,
                                             queryset=Manufacturer.objects.all(),
                                             widget=forms.Select(attrs={'class': 'form-control'}))


class AppSearchForm(forms.Form):
    # forms.CharField()
    article = forms.CharField(label='Артикул', widget=forms.TextInput(attrs={'autofocus': True,
                                                                             'class': 'form-control',
                                                                             'placeholder': "Введите артикул товара"
                                                                             }),
                              help_text="", error_messages={"has_errors": False})
    manufacturer_from = forms.ModelChoiceField(label='Исходный производитель', empty_label=None,
                                               queryset=Manufacturer.objects.all(),
                                               widget=forms.Select(attrs={'class': 'form-control'}))
    manufacturer_to = forms.ModelChoiceField(label='Необходимый производитель', empty_label=None,
                                             queryset=Manufacturer.objects.all(),
                                             widget=forms.Select(attrs={'class': 'form-control'}))


class FeedBackForm(forms.Form):
    name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': "Имя"
    }))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': "Email"
    }))
    phone = forms.CharField(label='Телефон', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': "Номер телефона"
    }))
    text = forms.CharField(label='Текст', widget=forms.Textarea(attrs={
        'class': 'form-control textarea',
        'rows': 5,
        'placeholder': "Ваше сообщение"
    }))

    
class SubscribeForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': "Email"
    }))
    

class LoginForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('user',)
