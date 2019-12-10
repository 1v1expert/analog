from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout, models

from catalog.utils import SearchProducts
from catalog.handlers import result_api_processing
from catalog.internal.utils import get_attributes, ProductInfo
from catalog.forms import SearchForm, AdvancedSearchForm
from catalog.models import Product


from app.models import MainLog, FeedBack
from app.decorators import a_decorator_passing_logs
from app.decorators import check_recaptcha
from app.forms import FeedBackForm, SubscribeForm
from catalog.internal.auth_actions import registration
from catalog.internal.utils import get_product_info


@csrf_exempt
@a_decorator_passing_logs
def search_from_form(request) -> HttpResponse:

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            
            article = form.cleaned_data['article']
            manufacturer_to = form.cleaned_data['manufacturer_to']
            product = Product.objects.filter(article=article).first()
            if not product:
                return JsonResponse(
                    {'result': [],
                     'error': 'Артикул %s не найден' % article
                     }, content_type='application/json')
            else:
                if product.raw is not None:
                    analogs = product.raw.get('analogs', None)
                    if analogs:
                        result_pk = analogs.get(manufacturer_to.title)
                        if result_pk is not None:
                            result = Product.objects.get(pk=result_pk)
                            return JsonResponse({
                                'result': [result.article],
                                'info': get_product_info(result),
                                'error': False
                            })
                return JsonResponse({'result': [], 'error': 'Аналог не найден'})
                
        return JsonResponse({'error': 'Некорректно заполненные данные.'})
    
    return JsonResponse({'result': [], 'error': "Некорректный запрос поиска"})


@a_decorator_passing_logs
def search_article(request) -> HttpResponse:
    
    article = request.GET.get('article', None)
    
    if len(article) > 1 and article is not None:
        return JsonResponse(list(
            Product.objects
                .filter(article__istartswith=article)
                .extra(select={'value': 'article'})
                .values('value', 'title', 'manufacturer__title')[:50]
        ), safe=False)
    
    return JsonResponse({'error': "Некорректный запрос"})


def advanced_search(request) -> HttpResponse:
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            article = form.cleaned_data['article']
            manufacturer_from = form.cleaned_data['manufacturer_from']
            manufacturer_to = form.cleaned_data['manufacturer_to']
            try:
                product = Product.objects.get(article=article, manufacturer=manufacturer_from)
            except Product.DoesNotExist:
                MainLog(user=request.user,
                        message='По артикулу: {} и производителю: {} не найдено товара'.
                        format(article, manufacturer_from)
                        ).save()
                return JsonResponse({'result': [], 'error': "Не найден продукт"}, content_type='application/json')
            except Product.MultipleObjectsReturned:
                MainLog(user=request.user,
                        message='По артикулу: {} и производителю: {} найдено несколько товаров'.format(article,
                                                                                                       manufacturer_from)).save()
                return JsonResponse({'result': [], 'error': "Найдено несколько продуктов, уточните поиск"})
            attributes_array = ProductInfo(product=product).get_attributes()
            advanced_form = AdvancedSearchForm(request.POST, extra=attributes_array.get('attributes'))
            if advanced_form.is_valid():
                advanced_form.cleaned_data['manufacturer_from'] = product.manufacturer
                advanced_form.cleaned_data['manufacturer_to'] = manufacturer_to
                MainLog(user=request.user,
                        message='По артикулу: {} и производителю: {} запрошен расширенный поиск: {}'.format(article,
                                                                                                            manufacturer_from,
                                                                                                            advanced_form.cleaned_data)).save()
                result = SearchProducts(request, advanced_form)
                return result_api_processing(result, request, default=False)
            else:
                MainLog(user=request.user,
                        message='Произошла ошибка при расширенном поиске по артикулу: {} и производителю: {}'.format(
                            article,
                            manufacturer_from)).save()
                return render(request, 'admin/catalog/search.html', {'error': 'Ошибка формы'})
        MainLog(user=request.user,
                message='Произошла ошибка при расширенном поиске, невалидная форма').save()
        return render(request, 'admin/catalog/search.html', {'error': 'Ошибка формы'})
    MainLog(message='Неверный тип запроса расширенного поиска').save()
    return JsonResponse({'result': [], 'error': "Произошла ошибка при выполнении запроса"})


def check_product_and_get_attributes(request) -> HttpResponse:
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            pi = ProductInfo(form=form)
            try:
                return JsonResponse({'result': pi.get_attributes(), 'error': False})
            except Product.DoesNotExist:
                return JsonResponse({'error': 'Не найдено продукта, удовл. критериям'})
            except Product.MultipleObjectsReturned:
                return JsonResponse({'error': 'Найдено несколько продуктов, уточн. поиск'})
            except Exception as e:
                MainLog.objects.create(user=request.user, raw={'error': e})
                return JsonResponse({'error': 'Произошла ошибка, обратитесь в тех. поддержку'})
    
    return HttpResponseBadRequest()


@a_decorator_passing_logs
@check_recaptcha
def feedback(request) -> HttpResponse:
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        user = request.user
        if str(request.user) == 'AnonymousUser':
            user = None
        if form.is_valid():
            
            if not request.recaptcha_is_valid:
                return JsonResponse({'OK': False, 'error': 'Invalid reCAPTCHA. Please try again.'})
            
            try:
                FeedBack.objects.create(user=user,
                                        text=form.cleaned_data.get('text', ''),
                                        email=form.cleaned_data.get('email', ''),
                                        name=form.cleaned_data.get('name', ''),
                                        phone=form.cleaned_data.get('phone', ''),
                                        )
                return JsonResponse({})
            except Exception as e:
                MainLog.objects.create(user=user, raw={'error': e}, has_errors=True)
                return HttpResponseBadRequest()
    return HttpResponseBadRequest()


@a_decorator_passing_logs
def subscriber(request) -> HttpResponse:
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        user = request.user
        if str(request.user) == 'AnonymousUser':
            user = None
        if form.is_valid():
            try:
                FeedBack.objects.create(user=user,
                                        email=form.cleaned_data.get('email', ''),
                                        is_subscriber=True
                                        )
                return JsonResponse({"OK": True})
            except Exception as e:
                MainLog.objects.create(user=user, raw={'error': e}, has_errors=True)
                return HttpResponseBadRequest()
    return HttpResponseBadRequest()


@a_decorator_passing_logs
def logout_view(request) -> HttpResponse:
    logout(request)
    return redirect('app:landing_home')


@a_decorator_passing_logs
def login_view(request) -> HttpResponse:
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        try:
            user = models.User.objects.get(username=username)
            if not user.check_password(password):
                return JsonResponse({'OK': False, 'error': 'Неверно введён логин или пароль'})
        except (models.User.DoesNotExist, models.User.MultipleObjectsReturned) as e:
            return HttpResponse('Unauthorized', status=401)
        
        if user.is_active:
            login(request, user)
            return JsonResponse({'OK': True})
        else:
            return JsonResponse({'OK': False, 'error': 'Учётная запись не подтверждена'})
            
    return HttpResponseBadRequest()

    
@a_decorator_passing_logs
def registration_view(request) -> HttpResponse:
    if request.method == 'POST':
        suc, text = registration(request=request)
        if suc:
            return JsonResponse({'OK': True})
        
        return JsonResponse({'OK': False, 'error': text})
    
    return HttpResponseBadRequest()
