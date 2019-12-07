from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate, login, logout, models, forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.mail import get_connection, send_mail
from django.conf import settings

from catalog.models import DataFile, Manufacturer
from catalog import choices
from catalog.handlers import ProcessingSearchFile
from catalog.internal.auth_actions import registration
from catalog.internal.messages import send_email_with_connection

from app.forms import \
    MyAuthenticationForm, MyRegistrationForm, AppSearchForm, SearchFromFile, EmailConfirmationForm, FeedBackForm, SubscribeForm
from app.decorators import a_decorator_passing_logs
from app.models import MainLog

from smtplib import SMTPDataError

import hashlib


@a_decorator_passing_logs
def login_view(request):
    auth_form = MyAuthenticationForm(request)
    if request.method == 'POST':
        username, password = request.POST['username'], request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                # HttpResponseRedirect
                redirect_cookie = redirect('app:home')
                redirect_cookie.set_signed_cookie("user2", "demo")
                return redirect_cookie
            
        return render(request, 'login.html', {'auth_form': auth_form, 'error': 'Неверно введён логин или пароль'})
    
    return render(request, 'login.html', {'auth_form': auth_form})


@a_decorator_passing_logs
@login_required(login_url='login/')
def search(request):
    form = AppSearchForm()
    
    if request.method == 'POST':
        form = AppSearchForm(request.POST)
    
    return render(request, 'search.html', {'user': request.user, 'form': form})


@login_required(login_url='login/')
@a_decorator_passing_logs
def search_from_file_view(request):

    if request.method == 'POST':
        form = SearchFromFile(request.POST, request.FILES)
        if form.is_valid():
            instance = DataFile(file=request.FILES['file'],
                                type=choices.TYPES_FILE[1][0],
                                created_by=request.user,
                                updated_by=request.user)
            instance.save()
            file_response = ProcessingSearchFile(request.FILES['file'], instance.file, form, request).file_search()
            
            message = u'Скачать результат подбора вы можете по ссылке: \n %s' \
                      % 'http://analogpro.ru/' + file_response.url
            try:
                send_email_with_connection(
                    'Результат подбора',
                    message,
                    [request.user.email])
            except SMTPDataError as e:
                pass
            return JsonResponse({'OK': True, 'file': file_response.url})
        else:
            return JsonResponse({'OK': False, 'error': 'Not valid form'})
            
    else:
        form = SearchFromFile()
        return render(request, 'search_from_file.html', {'form': form})


@a_decorator_passing_logs
@login_required(login_url='login/')
def advanced_search(request):
    return redirect('catalog:search')


@a_decorator_passing_logs
def check_in_view(request):
    reg_form = MyRegistrationForm()
    if request.method == 'POST':
        suc, resp = registration(request)
        if suc:
            return redirect('app:email_confirmation', resp.pk, resp.pk)
        
        return render(request, 'check_in.html', {'reg_form': reg_form, 'error': resp})
    
    return render(request, 'check_in.html', {'reg_form': reg_form})


# @login_required(redirect_field_name='app:login')
@login_required(login_url='login/')
@a_decorator_passing_logs
def home_view(request) -> HttpResponse:
    return render(request, 'home.html')


@login_required(login_url='login/')
@a_decorator_passing_logs
def profile_view(request) -> HttpResponse:
    return render(request, 'profile.html',
                  {
                      'actions_count': MainLog.objects.filter(user=request.user).count(),
                      'search_count': MainLog.objects.filter(user=request.user, message__icontains='search').filter(
                          message__icontains='post').count(),
                      'files_count': DataFile.objects.filter(created_by=request.user).count(),
                      'files': DataFile.objects.filter(created_by=request.user)})


@login_required(login_url='login/')
@a_decorator_passing_logs
def faq_view(request) -> HttpResponse:
    return render(request, 'faq.html')


@login_required(login_url='login/')
@a_decorator_passing_logs
def partners_view(request) -> HttpResponse:
    return render(request, 'to_partners.html')


@login_required(login_url='login/')
@a_decorator_passing_logs
def contacts_view(request) -> HttpResponse:
    return render(request, 'contacts.html')


@a_decorator_passing_logs
def logout_view(request) -> HttpResponse:
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
        return render(request, 'email_confirmation.html', {'confirmation': True, 'msg': msg})
    
    elif verification_code == user_id:
        confirmation_form = EmailConfirmationForm()
        if request.method == 'POST':
            confirmation_form = EmailConfirmationForm(request)
            if check_code == request.POST['code']:
                user.is_active = True
                user.save()
                msg = 'E-mail подтверждён'
                return render(request, 'email_confirmation.html',
                              {'confirmation': True, 'msg': msg})
            else:
                msg = 'Код неверен'
        return render(request, 'email_confirmation.html', {'conf_form': confirmation_form, 'msg': msg})
    return render(request, 'email_confirmation.html', {'msg': "Ошибка подтверждения email'a"})

#  ========================
#  Landing page, new design
#  ========================


@a_decorator_passing_logs
def landing_page_view(request) -> HttpResponse:
    """  The function renders the main project page """
    # https://ianlunn.github.io/Hover/
    feedback_form = FeedBackForm()
    auth_form = MyAuthenticationForm(request)
    reg_form = MyRegistrationForm()
    subscribe_form = SubscribeForm()
    manufacturers = Manufacturer.objects.filter(is_tried=True)
    return render(request, 'landing_page.html', {
        'manufacturers': manufacturers,
        'feedback': feedback_form,
        'auth_form': auth_form,
        'reg_form': reg_form,
        'subscribe_form': subscribe_form,
        # 'error': error
    })


@a_decorator_passing_logs
def landing_confirm_mail_page(request, verification_code, user_id) -> HttpResponse:
    """  The function renders the main project page with mail confirmation """
    user = get_object_or_404(models.User, pk=user_id)
    check_code = hashlib.md5('{}'.format(user.pk).encode()).hexdigest()
    feedback_form = FeedBackForm()
    auth_form = MyAuthenticationForm(request)
    reg_form = MyRegistrationForm()
    manufacturers = Manufacturer.objects.all()
    args = {
        'manufacturers': manufacturers,
        'feedback': feedback_form,
        'auth_form': auth_form,
        'reg_form': reg_form,
        'confirm_email': True
        # 'error': error
    }
    if verification_code == check_code and user:
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'landing_page.html', args)
    else:
        args['confirm_email'] = False
        return render(request, 'landing_page.html', args)