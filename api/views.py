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
    # print(vars(request), request.method, request.method.POST)
    if request.method == 'POST':
        form = SearchForm(request.POST)
        # print( 'POST')
        if form.is_valid():
            # article = form.cleaned_data['article']
            # manufacturer_from = form.cleaned_data['manufacturer_from']
            
            # resp = check_product(article, manufacturer_from)
            
            # if resp.get('correctly'):
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
                            }, content_type='application/json')
                return JsonResponse(
                    {'result': [],
                     'error': 'Аналог не найден'
                     }, content_type='application/json')
                    
            # result = SearchProducts(form=form)
            # return result_api_processing(result, request, default=True)
        
        
        # else:
        # MainLog(user=request.user, message=resp['error_system']
        #         ).save()
        # return JsonResponse(resp, content_type='application/json')
        
        return JsonResponse({'error': 'Некорректно заполненные данные.'}, content_type='application/json')
    # return render(request, 'admin/catalog/search.html', {'error': 'Ошибка формы'})
    
    return JsonResponse({'result': [], 'error': "Некорректный запрос поиска"},
                        content_type='application/json')


@a_decorator_passing_logs
def search_article(request) -> HttpResponse:
    
    article = request.GET.get('article', None)
    
    if len(article) > 1 and article is not None:
        return JsonResponse(list(
            Product.objects
                .filter(article__istartswith=article)
                .extra(select={'value': 'article'})
                .values('value', 'title', 'manufacturer__title')[:15]
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
                        message='По артикулу: {} и производителю: {} не найдено товара'.format(article,
                                                                                               manufacturer_from)).save()
                return JsonResponse({'result': [], 'error': "Не найден продукт"}, content_type='application/json')
            except Product.MultipleObjectsReturned:
                MainLog(user=request.user,
                        message='По артикулу: {} и производителю: {} найдено несколько товаров'.format(article,
                                                                                                       manufacturer_from)).save()
                return JsonResponse({'result': [], 'error': "Найдено несколько продуктов, уточните поиск"},
                                    content_type='application/json')
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
    return JsonResponse({'result': [], 'error': "Произошла ошибка при выполнении запроса"},
                        content_type='application/json')


# if request.method == 'POST':
# 	advanced_form = AdvancedSearchForm(request.POST, extra=attributes_array)
# 	if advanced_form.is_valid():
# 		advanced_form.cleaned_data['manufacturer_from'] = product.manufacturer
# 		advanced_form.cleaned_data['manufacturer_to'] = manufacturer_to

#
# return render(request, 'admin/catalog/advanced_search.html',
#               {'advanced_form': advanced_form, 'product': product, 'manufacturer_to': manufacturer_to})


def check_product_and_get_attributes(request) -> HttpResponse:
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            pi = ProductInfo(form=form)
            try:
                return JsonResponse({'result': pi.get_attributes(), 'error': False}, content_type='application/json')
            except Product.DoesNotExist:
                return JsonResponse({'error': 'Не найдено продукта, удовл. критериям'}, content_type='application/json')
            except Product.MultipleObjectsReturned:
                return JsonResponse({'error': 'Найдено несколько продуктов, уточн. поиск'}, content_type='application/json')
            except Exception as e:
                MainLog.objects.create(user=request.user, raw={'error': e})
                return JsonResponse({'error': 'Произошла ошибка, обратитесь в тех. поддержку'}, content_type='application/json')
    
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
                return JsonResponse({'OK': False, 'error': 'Invalid reCAPTCHA. Please try again.'}, content_type='application/json')
            
            try:
                FeedBack.objects.create(user=user,
                                        text=form.cleaned_data.get('text', ''),
                                        email=form.cleaned_data.get('email', ''),
                                        name=form.cleaned_data.get('name', ''),
                                        phone=form.cleaned_data.get('phone', ''),
                                        )
                return JsonResponse({}, content_type='application/json')
            except Exception as e:
                MainLog.objects.create(user=user, raw={'error': e}, has_errors=True)
                return HttpResponseBadRequest()
    return HttpResponseBadRequest()
    # return JsonResponse({'error': 'error'}, content_type='application/json')


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
                return JsonResponse({"OK": True}, content_type='application/json')
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
    # auth_form = MyAuthenticationForm(request)
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        try:
            user = models.User.objects.get(username=username)
            if not user.check_password(password):
                return JsonResponse({'OK': False, 'error': 'Неверно введён логин или пароль'})
        except (models.User.DoesNotExist, models.User.MultipleObjectsReturned) as e:
            return HttpResponse('Unauthorized', status=401)
        
        # user = authenticate(request, username=username, password=password)
        if user.is_active:
            login(request, user)
            # return redirect('app:landing_home')
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
