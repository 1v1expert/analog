from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

from catalog.utils import SearchProducts
from catalog.handlers import result_api_processing
from catalog.internal.utils import get_attributes
from catalog.forms import SearchForm, AdvancedSearchForm
from catalog.models import Product, FixedValue

from app.models import MainLog
from app.decorators import a_decorator_passing_logs


def check_product(article, manufacturer_from) -> dict:
    response = {'result': []}
    
    try:
        product = Product.objects.get(article=article, manufacturer=manufacturer_from)
        return {'correctly': True,
                'product': product}
    
    except Product.DoesNotExist as e:
        # response['correctly'] = False
        response['error_system'] = 'article: {}; manufacturer_from: {}; {}'.format(article, manufacturer_from, e)
        response['error'] = 'По артикулу: {} и производителю: {} товара не найдено'.format(article, manufacturer_from)
    
    except Product.MultipleObjectsReturned as e:
        # response['correctly'] = False
        response['error_system'] = 'article: {}; manufacturer_from: {}; {}'.format(article, manufacturer_from, e)
        response['error'] = "Найдено несколько продуктов, уточните поиск"
    
    return response


@csrf_exempt
@a_decorator_passing_logs
def search_from_form(request):
    # print(vars(request), request.method, request.method.POST)
    if request.method == 'POST':
        form = SearchForm(request.POST)
        # print( 'POST')
        if form.is_valid():
            # article = form.cleaned_data['article']
            # manufacturer_from = form.cleaned_data['manufacturer_from']
            
            # resp = check_product(article, manufacturer_from)
            
            # if resp.get('correctly'):
            
            result = SearchProducts(request, form)
            return result_api_processing(result, request, default=True)
        # else:
        # MainLog(user=request.user, message=resp['error_system']
        #         ).save()
        # return JsonResponse(resp, content_type='application/json')
        
        return JsonResponse({'error': 'not valid form'}, content_type='application/json')
    # return render(request, 'admin/catalog/search.html', {'error': 'Ошибка формы'})
    
    return JsonResponse({'result': [], 'error': "Произошла ошибка при выполнении запроса"},
                        content_type='application/json')


def advanced_search(request):
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
            attributes_array = get_attributes(product)
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


def check_product_and_get_attributes(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            article = form.cleaned_data['article']
            manufacturer_from = form.cleaned_data['manufacturer_from']
            
            resp = check_product(article, manufacturer_from)
            
            if resp['correctly']:
                attributes_array = get_attributes(resp['product'])
                return JsonResponse({'result': attributes_array, 'error': False}, content_type='application/json')
            else:
                MainLog(user=request.user, message=resp['error_system']).save()
                return JsonResponse(resp, content_type='application/json')
    
    return JsonResponse({"success": True}, content_type='application/json')
