from catalog.file_utils import XLSDocumentReader
from catalog.models import Product, DataFile
from catalog.utils import SearchProducts
from catalog import choices

from reporters.writers import BookkeepingWriter
from reporters.writers import dump_csv

import csv

from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse


def loaded_search_file_handler(file, path, form, request):
	content = XLSDocumentReader(path=path).parse_file()
	manufacturer_from = form.cleaned_data['manufacturer_from']

	result_content = []
	for i, rec in enumerate(content):
		body = []
		if i:
			body.append(rec.get(0))
			try:
				product = Product.objects.get(article=rec.get(0), manufacturer=manufacturer_from)
			except Product.DoesNotExist:
				body.append('Not found product with article {} and manufacturer {}'.format(rec.get(0), manufacturer_from))
				result_content.append(body)
				continue
			except Product.MultipleObjectsReturned:
				body.append(
					'Found any product with article {} and manufacturer {}'.format(rec.get(0), manufacturer_from))
				result_content.append(body)
				continue
			
			instance = SearchProducts(request, form, product)
			instance.global_search(default=True)
			
			if instance.founded_products.count():
				if instance.founded_products.count() == 1:
					body.append(instance.founded_products.get().article)
				else:
					for f_pr in instance.founded_products:
						body.append(f_pr.article)
			else:
				body.append('not found a product that meets the criteria')
			
			result_content.append(body)
			
	filename = 'OUT_{}.csv'.format(path.name[6:-5])
	
	dump_csv(filename, result_content)
	instance = DataFile(type=choices.TYPES_FILE[2][0], created_by=request.user, updated_by=request.user)
	instance.file.name = 'files/{}'.format(filename)
	instance.save()
	
	# with open('{}/{}'.format(settings.FILES_ROOT, filename), 'w', newline='', encoding='utf-8') as csvfile:
	# 	writer = csv.writer(csvfile, dialect='excel')
	# 	for row in result_content:
	# 		writer.writerow(row)

		# instance.file = csvfile
		
		# instance.file.path = '{}/{}'.format(settings.FILES_ROOT, filename)
		# instance.save()
	return instance.file


def result_processing(instance, request, product, default=True):
	instance.global_search(default=default)
	if instance.founded_products.count():
		if instance.founded_products.count() == 1:
			error = {'val': False}
		else:
			error = {'val': True, 'msg': 'Найдено более одного продукта, подходящего по параметрам поиска {}'}
		return render(request, 'admin/catalog/search.html',
		              {'Results': instance.founded_products, 'Product': product, 'Error': error, 'Lead_time': instance.lead_time})
	else:
		error = {'val': True, 'msg': 'Продукты, удовлетворяющие параметрам поиска, не найдены'}
		return render(request, 'admin/catalog/search.html',
		              {'Results': instance.founded_products, 'Product': product, 'Error': error, 'Lead_time': instance.lead_time})


def result_api_processing(instance, request, product, default=True):
	instance.global_search(default=default)
	if instance.founded_products.count():
		if instance.founded_products.count() == 1:
			error = False
		else:
			error = 'Найдено более одного продукта, подходящего по параметрам поиска'
		return JsonResponse(
			{'result': [prod.article for prod in instance.founded_products],
			 'error': error, 'Lead_time': instance.lead_time}, content_type='application/json')
	else:
		error = 'Продукты, удовлетворяющие параметрам поиска, не найдены'
		return JsonResponse(
			{'result': [], 'error': error,
			 'Lead_time': instance.lead_time}, content_type='application/json')