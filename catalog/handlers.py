from catalog.file_utils import XLSDocumentReader
from catalog.models import Product, DataFile
from catalog.utils import SearchProducts
from catalog import choices
from catalog.internal.utils import get_product_info

from app.models import MainLog

from catalog.reporters.writers import dump_csv, BookkeepingWriter

import csv

from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse


class NewProcessingSearchFile(object):
    def __init__(self, input_file, user):
        self.file = None
        self.input_file = input_file
        self.user = user

    def save(self, file, user):
        self.file = DataFile(file=file,
                             type=choices.TYPES_FILE[1][0],
                             created_by=user,
                             updated_by=user)
        self.file.save()
        return self.file
      
    def read_file(self):
        if self.file is not None:
            return XLSDocumentReader(path=self.file.file).parse_file()
        
        raise
    
    def process(self):
        self.save()


class ProcessingSearchFile:
    def __init__(self, file, path, form, request, type='csv'):
        self.path = path
        self.form = form
        self.request = request
        self.content = XLSDocumentReader(path=path).parse_file()
        self.manufacturer_from = form.cleaned_data['manufacturer_from']
        
    @staticmethod
    def check_product(article, manufacturer):
        if manufacturer is None:
            products = Product.objects.filter(article=article)
        else:
            products = Product.objects.filter(article=article, manufacturer=manufacturer)
            
        if products.exists():
            return products.first(), ''
        else:
            return None, u'Not found product with article %s' % article
    
    def file_search(self, data=None):
        if not data:
            data = self.content
        result_content = []
        for i, rec in enumerate(data):
            body = list()
            
            body.append(rec.get(0))
            body.append(rec.get(1))
            product, err = self.check_product(rec.get(0), self.manufacturer_from)
            
            if product is None:
                body.append(err)
                result_content.append(err)
                continue
            
            instance = SearchProducts(self.request, self.form, product)
            instance.global_search(default=True)
            
            if instance.founded_products.count():
                body.append(instance.founded_products.first().article)
            else:
                body.append('not found a product that meets the criteria')
            
            result_content.append(body)
        
        filename = 'OUT_{}.xls'.format(self.path.name[6:-5])
        
        dump_csv(filename, result_content)
        instance = DataFile(type=choices.TYPES_FILE[2][0], created_by=self.request.user, updated_by=self.request.user)
        instance.file.name = 'files/{}'.format(filename)
        instance.save()
        
        return instance.file


def result_processing(instance, request, product, default=True):
    instance.global_search(default=default)
    if instance.founded_products.count():
        if instance.founded_products.count() == 1:
            error = {'val': False}
        else:
            error = {'val': True, 'msg': 'Найдено более одного продукта, подходящего по параметрам поиска {}'}
        return render(request, 'admin/catalog/search.html',
                      {'Results': instance.founded_products, 'Product': product, 'Error': error,
                       'Lead_time': instance.lead_time})
    else:
        error = {'val': True, 'msg': 'Продукты, удовлетворяющие параметрам поиска, не найдены'}
        return render(request, 'admin/catalog/search.html',
                      {'Results': instance.founded_products, 'Product': product, 'Error': error,
                       'Lead_time': instance.lead_time})


def result_api_processing(instance, request, default=True):
    # try:
    user = request.user
    if str(request.user) == 'AnonymousUser':
        user = None
    instance.global_search(default=default)
    # except Exception as e:
    # 	print(e)
    if instance.error:
        error = 'Ошибка'
        return JsonResponse(
            {'result': [], 'error': error}, content_type='application/json')
    
    number_of_products_found = instance.founded_products.count()
    if number_of_products_found:
        # if number_of_products_found == 1:
        # 	error = False
        # else:
        # 	error = False
        # error = 'Найдено более одного продукта, подходящего по параметрам поиска'
        
        MainLog(user=user, message='Поиск выполнился за {}c., найдено {}'.format(instance.lead_time,
                                                                                 [prod.article for prod in
                                                                                  instance.founded_products])).save()
        # founded products must be one
        founded_product = instance.founded_products.first()
        return JsonResponse(
            {'result': [founded_product.article], 'info': get_product_info(founded_product),
             # {'result': [prod.article for prod in instance.founded_products[:1]],
             'error': False, 'Lead_time': instance.lead_time}, content_type='application/json')
    else:
        MainLog(user=user,
                message='Поиск выполнился за {}c., продуктов, удовлетворяющих параметрам поиска, не найдено'.format(
                    instance.lead_time)).save()
        error = 'Продукты, удовлетворяющие параметрам поиска, не найдены'
        return JsonResponse(
            {'result': [], 'error': error,
             'Lead_time': instance.lead_time}, content_type='application/json')
