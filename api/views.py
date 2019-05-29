from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import json
from catalog.forms import SearchForm, AdvancedSearchForm
from catalog.choices import TYPES_SEARCH
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
			# manufacturer_to = form.cleaned_data['manufacturer_to']
			
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


def advanced_search(request):
	return redirect('catalog:search')


def get_product(request):
	print('Point into api request')
	# print(vars(request.POST), '\n', vars(request.GET), '\n', vars(request))
	if request.method == 'POST':
		form = SearchForm(request.POST)
		if form.is_valid():
			article = form.cleaned_data['article']
			manufacturer_from = form.cleaned_data['manufacturer_from']
			
			try:
				product = Product.objects.get(article=article, manufacturer=manufacturer_from)
			except Product.DoesNotExist:
				return JsonResponse({'result': [], 'error': "Не найден продукт"}, content_type='application/json')
				# return render(request, 'admin/catalog/search.html',
				#               {'Error': {'val': True, 'msg': 'Не найден продукт с артикулом {}'.format(article)}})
			except Product.MultipleObjectsReturned:
				return JsonResponse({'result': [], 'error': "Найдено несколько продуктов, уточните поиск"}, content_type='application/json')
				# return render(request, 'admin/catalog/search.html',
				#               {'Error': {'val': True, 'msg': 'Найдено более одного продукта с артикулом {}'
				#                                              'и производителем {}'.format(article, manufacturer_from)}})
			
			fix_attributes = product.fixed_attrs_vals.all()  # category.attributes.all()
			unfix_attributes = product.unfixed_attrs_vals.all()  # category.attributes.all()
			# attributes = product.attrs_vals.all()
			# attributes_array = {str(attr.pk): {'title': attr.title,
			#                                    'type_display': attr.get_type_display(),
			#                                    'attribute': attr,
			#                                    'type': attr.type} for attr in attributes}
			attributes_array = {
				'fix' + str(attr.pk): {'title': attr.attribute.title, 'type_display': attr.attribute.get_type_display(),
				                       'choices': [(at.pk, at.title) for at in FixedValue.objects.filter(attribute=attr.attribute)]
					                       # serializers.serialize('json',
				                            #                             FixedValue.objects.filter(attribute=attr.attribute),
				                            #                             fields=('pk', 'title'))
				                                                        # .values_list('pk', 'title'))
,
				                       # 'choices': [attribute.title for attribute in FixedValue.objects.filter(attribute=attr.attribute)],
				                       'type': attr.attribute.type} for attr in fix_attributes}
			
			# fix_attributes_array = {
			# 'fix' + str(attr.pk): {'title': attr.attribute.title, 'type_display': attr.attribute.get_type_display(),
			#                        'choices': FixedValue.objects.filter(attribute=attr.attribute).values_list('pk',
			#                                                                                                   'title'),
			#                        # 'choices': [attribute.title for attribute in FixedValue.objects.filter(attribute=attr.attribute)],
			#                        'type': attr.attribute.type} for attr in fix_attributes}
			
			unfix_attributes_array = {'unfix' + str(attr.pk): {'title': attr.attribute.title,
			                                                   'type_display': attr.attribute.get_type_display(),
			                                                   'choices': TYPES_SEARCH,
			                                                   # 'choices': [attribute.title for attribute in FixedValue.objects.filter(attribute=attr.attribute)],
			                                                   'type': attr.attribute.type} for attr in
			unfix_attributes}
			
			# attributes_array.update(fix_attributes_array)
			attributes_array.update(unfix_attributes_array)
			

			# advanced_form = AdvancedSearchForm(extra=attributes_array, initial=data)
			return JsonResponse({'result': attributes_array, 'error': False}, content_type='application/json')
		# 	return list attrs
		else:
			print('Unvalid form')
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