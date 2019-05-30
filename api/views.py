from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import json
from catalog.forms import SearchForm, AdvancedSearchForm
from catalog.choices import TYPES_SEARCH, TYPES, TYPES_REV_DICT, TYPES_DICT
from catalog.models import Product, FixedValue
from django.core import serializers
from catalog.utils import SearchProducts
from catalog.handlers import result_api_processing


def search(request):
	if request.method == 'POST':
		form = SearchForm(request.POST)
		if form.is_valid():
			article = form.cleaned_data['article']
			manufacturer_from = form.cleaned_data['manufacturer_from']

			try:
				product = Product.objects.get(article=article, manufacturer=manufacturer_from)
			except Product.DoesNotExist:
				return JsonResponse({'result': [], 'error': "Не найден продукт"}, content_type='application/json')
			except Product.MultipleObjectsReturned:
				return JsonResponse({'result': [], 'error': "Найдено несколько продуктов, уточните поиск"},
				                    content_type='application/json')
			
			result = SearchProducts(request, form, product)
			return result_api_processing(result, request, product, default=True)  # return SearchProducts(request, form, product).search()
		
		return render(request, 'admin/catalog/search.html', {'error': 'Ошибка формы'})
	
	return JsonResponse({'result': [], 'error': "Произошла ошибка при выполнении запроса"}, content_type='application/json')


def get_attributes(product, api=True):
	fix_attributes = product.fixed_attrs_vals.all()  # category.attributes.all()
	unfix_attributes = product.unfixed_attrs_vals.all()  # category.attributes.all()
	attributes_array = {
		'fix' + str(attr.pk): {'title': attr.attribute.title, 'type_display': attr.attribute.get_type_display(),
		                       'choices': [(at.pk, at.title) for at in
		                                   FixedValue.objects.filter(attribute=attr.attribute)]
		                       # serializers.serialize('json',
		                       #                             FixedValue.objects.filter(attribute=attr.attribute),
		                       #                             fields=('pk', 'title'))
		                       # .values_list('pk', 'title'))
			, # 'choices': [attribute.title for attribute in FixedValue.objects.filter(attribute=attr.attribute)],
			                   'type': attr.attribute.type} for attr in fix_attributes}
	unfix_attributes_array = {
	'unfix' + str(attr.pk): {'title': attr.attribute.title, 'type_display': attr.attribute.get_type_display(),
	                         'choices': TYPES_SEARCH, 'type': attr.attribute.type} for attr in unfix_attributes}
	
	attributes_array.update(unfix_attributes_array)
	
	# types = set(product.category.attributes.all().values_list('type',  flat=True))
	response = {'attributes': attributes_array, 'product_types': list((type_[0] for type_ in TYPES)), 'all_types': TYPES_DICT}
	# print(response, '\n\n', TYPES_REV_DICT, '\n\n', TYPES_DICT)
	# attributes_array.update()
	# print(attributes_array, '\n', list(types))
	return response


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
				return JsonResponse({'result': [], 'error': "Не найден продукт"}, content_type='application/json')
			except Product.MultipleObjectsReturned:
				return JsonResponse({'result': [], 'error': "Найдено несколько продуктов, уточните поиск"},
				                    content_type='application/json')
			attributes_array = get_attributes(product)
			advanced_form = AdvancedSearchForm(request.POST, extra=attributes_array.get('attributes'))
			if advanced_form.is_valid():
				advanced_form.cleaned_data['manufacturer_from'] = product.manufacturer
				advanced_form.cleaned_data['manufacturer_to'] = manufacturer_to
				result = SearchProducts(request, advanced_form, product)
				return result_api_processing(result, request, product, default=False)
			else:
				return render(request, 'admin/catalog/search.html', {'error': 'Ошибка формы'})

		return render(request, 'admin/catalog/search.html', {'error': 'Ошибка формы'})
	
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


def get_product(request):
	if request.method == 'POST':
		form = SearchForm(request.POST)
		if form.is_valid():
			article = form.cleaned_data['article']
			manufacturer_from = form.cleaned_data['manufacturer_from']
			
			try:
				product = Product.objects.get(article=article, manufacturer=manufacturer_from)
			except Product.DoesNotExist:
				return JsonResponse({'result': [], 'error': "Не найден продукт"}, content_type='application/json')
			except Product.MultipleObjectsReturned:
				return JsonResponse({'result': [], 'error': "Найдено несколько продуктов, уточните поиск"}, content_type='application/json')
				
			attributes_array = get_attributes(product)
			return JsonResponse({'result': attributes_array, 'error': False}, content_type='application/json')
		# 	return list attrs
		else:
			return JsonResponse({'result': [], 'error': "Не найден продукт"}, content_type='application/json')
		# body_unicode = request.body.decode('utf-8')
		# ----
		# body = json.loads(request.body)
		# content = body['manufacturer_from']
		# print('POST', content)
	data = some_data_to_dump = {"success": True}
	# data = json.dumps(some_data_to_dump)
	# data = simplejson.dumps(some_data_to_dump)
	return JsonResponse(data, content_type='application/json')
	# return HttpResponse(json.dumps(some_data_to_dump), content_type='application/json')