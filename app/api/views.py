import json
import logging

from django.contrib.auth import login, logout, models
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from app.decorators import a_decorator_passing_logs
from app.decorators import check_recaptcha
from app.forms import FeedBackForm, SubscribeForm
from app.models import FeedBack, MainLog
from catalog.exceptions import AnalogNotFound, ArticleNotFound
from catalog.forms import AdvancedSearchForm, SearchForm
from catalog.handlers import result_api_processing
from catalog.internal.auth_actions import registration
from catalog.internal.utils import ProductInfo#, get_product_info
from catalog.models import Manufacturer, Product
from catalog.utils import SearchProducts

logger = logging.getLogger('analog')


# def get_product_info(analog, original=None):
#     info = [{"analog":
#                  {"name": "наименование", "value": analog.title},
#              "original":
#                  {"name": "наименование", "value": original.title}
#              }]
#
#     original_info = original.get_info()
#     analog_get_info = analog.get_info()
#
#     fixed_attributes = []  # for find images in groups
#
#     for attr in analog_get_info:
#         analog_name = attr.attribute.title
#         orig_attr = None
#
#         if analog_name in ('ед.изм', 'цена'):
#             continue
#
#         for original_attr in original_info:
#             print(original_attr.attribute.title, analog_name)
#             if original_attr.attribute.title == analog_name:
#                 orig_attr = original_attr
#                 break
#
#         analog_info = {'name': analog_name}
#
#         if attr.attribute.is_fixed:
#             analog_value = attr.value.title
#             original_value = orig_attr.value.title if orig_attr else ""
#             fixed_attributes.append(attr.value)  # for search group with image
#         else:
#             analog_value = attr.un_value
#             original_value = orig_attr.value if orig_attr else ""
#
#         analog_info['value'] = analog_value
#
#         info.append({"analog":
#                          {"name": analog_info["name"], "value": analog_info["value"]},
#                      "original":
#                          {"name": analog_info["name"], "value": original_value}
#                      })
#
#     info.append({"analog":
#                      {"name": "производитель", "value": analog.manufacturer.title},
#                  "original":
#                      {"name": "производитель", "value": original.manufacturer.title}
#                  })
#     # find group with image
#     if not len(fixed_attributes):
#         return {"result": info}
#
#     from catalog.models import GroupSubclass
#     try:
#         group = GroupSubclass.objects.get(category=analog.category,
#                                           fixed_attribute__in=fixed_attributes)
#         return {"result": info, "image": group.image.url}
#
#     except GroupSubclass.DoesNotExist:
#         pass
#     except GroupSubclass.MultipleObjectsReturned:
#         pass
#
#     return {"result": info}


def advanced_search(request: HttpRequest) -> HttpResponse:
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


def check_product_and_get_attributes(request: HttpRequest) -> HttpResponse:
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
def feedback(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        user = request.user if str(request.user) != 'AnonymousUser' else None
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
def subscriber(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        user = request.user if str(request.user) != 'AnonymousUser' else None
        if form.is_valid():
            try:
                obj, created = FeedBack.objects.get_or_create(
                    email=form.cleaned_data.get('email', ''),
                    is_subscriber=True,
                    defaults={"user": user}
                )
                if created:
                    return JsonResponse({"OK": True})
                else:
                    return JsonResponse({"OK": False})
            except Exception as e:
                MainLog.objects.create(user=user, raw={'error': e}, has_errors=True)
                return HttpResponseBadRequest()
    return HttpResponseBadRequest()


@a_decorator_passing_logs
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('app:landing_home')


@a_decorator_passing_logs
def login_view(request: HttpRequest) -> HttpResponse:
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
def registration_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        suc, text = registration(request=request)
        if suc:
            return JsonResponse({'OK': True})
        
        return JsonResponse({'OK': False, 'error': text})
    
    return HttpResponseBadRequest()


@csrf_exempt
def report_an_error(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        body['user'] = str(request.user)
        MainLog.objects.create(raw=body,
                               message='report_an_error')

        return JsonResponse({'OK': True})
    return HttpResponseBadRequest()
