from django.shortcuts import render
from .forms import *
from .models import Product, AttributeValue
from django.http.response import HttpResponse


def render_search(request, queryset):
	return render(request, 'admin/catalog/search.html', queryset)
# Create your views here.


class SearchProducts(object):
	def __init__(self, request, form):
		self.request = request
		self.manufacturer_from = form.cleaned_data['manufacturer_from']
		self.manufacturer_to = form.cleaned_data['manufacturer_to']
		self.article = form.cleaned_data['article']
		#self.product = None
		#self.products_found = None
		#self.product = None
	
	
	@staticmethod
	def finding_the_сlosest_attribute_value(need_attr, all_attr):
		# first_attr = need_attr.first()
		print(need_attr, need_attr)
		# all_attrr = all_attr.filter(attrs_vals__attribute__title=first_attr[1]) # title
		print('\n\n', all_attr)
		difference = None
		value = None
		for i, attr in enumerate(all_attr):
			if not i:
				difference = int(attr[0]) - int(need_attr.title)
				value = int(attr[0])
				continue
			if int(attr[0]) - int(need_attr.title) < difference:
				difference = int(attr[0]) - int(need_attr.title)
				value = int(attr[0])
		return value
	
	def search(self):
		
			#print(value, difference, '\n\n', all_attr)
		try:
			self.product = Product.objects.get(article=self.article, manufacturer=self.manufacturer_from)
		except Product.DoesNotExist:
			return render(self.request, 'admin/catalog/search.html', {
				'Error': {'val': True, 'msg': 'Не найден продукт с артикулом {}'.format(self.article)}})
		except Product.MultipleObjectsReturned:
			return render(self.request, 'admin/catalog/search.html',
			              {'Error': {'val': True, 'msg': 'Найдено более одного продукта с артикулом {}'
			                                             'и производителем {}'.format(self.article, self.manufacturer_from)}})
		# initial filter product
		print(self.manufacturer_to.pk, self.product.category.pk)
		self.products_found = Product.objects.filter(manufacturer=self.manufacturer_to, category__title=self.product.category.title)
		#print(self.products_found)
		# result2 = Product.objects.filter(manufacturer=self.manufacturer_to,
		#                                   category=self.product.category,
		#                                   #attrs_vals__attribute=attr.attribute,
		#                                   )
		sft_attrs = self.product.attrs_vals.filter(attribute__type='sft')
		hrd_attrs = self.product.attrs_vals.filter(attribute__type='hrd')
		print(hrd_attrs, sft_attrs, self.products_found)
		for attr in hrd_attrs:
			self.products_found = self.products_found.filter(attrs_vals__title=attr.title, attrs_vals__attribute=attr.attribute)
			print(attr.title, attr.attribute)
		if not self.products_found.count():
			print('Не найден ни один продукт по жестким атрибутам')
			pass # todo: make render with error | не найден продукт по жестким аттрибутам
		if self.products_found.count() == 1:
			pass # todo: make render response | успех
		else: # найдено более одного продукта по жестким
			middle_products_found = self.products_found
			
			for attr in sft_attrs:
				middle_products_found = middle_products_found.filter(attrs_vals__title=attr.title, attrs_vals__attribute=attr.attribute)
				if not middle_products_found.count():
					break
			if not middle_products_found.count():
				first_need_attr = sft_attrs.order_by('attribute__priority').first()
				
				#  берём первый мягкий аттрибут согласно его приоритету у товара по которому ищем
				value = self.finding_the_сlosest_attribute_value(first_need_attr, self.products_found.filter(
					attrs_vals__attribute__type='sft',
					attrs_vals__attribute__title=first_need_attr.attribute.title).values_list('attrs_vals__title',
				                                                                              'attrs_vals__attribute__title',
				                                                                              named=True))
				self.products_found = self.products_found.filter(attrs_vals__title=value, attrs_vals__attribute=first_need_attr.attribute)
			
			
		#print(result.attrs_vals.all())
		#print(result2.attrs_vals.all())
		# cycle for attributes in product attributes
		# for attr in self.product.attrs_vals.all():
		# 	# find_product = find_product.filter(attrs_vals__attribute=attr.attribute,
		# 	#                                    attrs_vals__title=attr.title)
		# 	if attr.attribute.type in ('hrd', 'sft'):
		# 		self.products_found = self.products_found.filter(attrs_vals__title=attr.title)
				#, )
		print(self.products_found)
		return self


def search_view(request):
	form = SearchForm()
	advanced_form = AdvancedeSearchForm()
	
	if request.method == 'POST':
		form = SearchForm(request.POST)
		if form.is_valid():
			# try:
			# проверка на единственность и существование продукта с артикулом и поставщиком
			result = SearchProducts(request, form).search()
			if isinstance(result, HttpResponse):
				return result
			if result.products_found.count() == 1:
				error = {'val': False}
			elif result.products_found.count() == 0:
				error = {'val': True, 'msg': 'По заданным параметрам не найдено продуктов'}
			else:
				error = {'val': True, 'msg': 'По заданным параметрам найдено более одного продукта'}
			return render(request, 'admin/catalog/search.html', {'Results': result.products_found, 'Product': result.product,
			                                                     'Error': error})
			# print(products_values, find_product)
			#print(product.category)
			#print(product.category.attributes.filter(type='hrd'))
			#find_product = Product.objects.filter(manufacturer=form.cleaned_data['manufacturer_to'])
			#print(find_product)
			# except Exception as e:
			# 	return render(request, 'admin/catalog/search.html', {'Error': {'val': True,
			# 	                                                               'msg': 'Произошла непредвиденная ошибка '
			# 	                                                                      'при поиске артикула {}, >> {}'.format(
			# 		                                                               form.cleaned_data['article'], e)}})
			#print(form.cleaned_data)
		return render(request, 'admin/catalog/search.html', {'Fake': 'Fake'})

	return render(request, 'admin/catalog/search.html', {'form': form, 'advanced_form': advanced_form}) #{'form': form})