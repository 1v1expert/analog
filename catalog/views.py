from django.shortcuts import render
from .forms import *
from .models import Product, AttributeValue, Category
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
		self.product = None
		self.products_found = None
		self.product = None
	
	@staticmethod
	def finding_the_сlosest_attribute_value(all_attr, step_attr):
		# first_attr = need_attr.first()
		# print(need_attr, need_attr)
		# # all_attrr = all_attr.filter(attrs_vals__attribute__title=first_attr[1]) # title
		# print(need_attr, '\n\n', all_attr, '\n\n', step_attr.title)
		# difference = None
		# value = None
		values_list = [float(attr.attrs_vals.get(attribute__type='sft', attribute__title=step_attr.attribute.title).title) for attr in all_attr]
		value = min(values_list, key=lambda x: abs(x-float(step_attr.title)))
		print(values_list, )
		return value
		# for i, attr in enumerate(all_attr):
		# 	values_list = []
		# 	ttr =
		# 	print(ttr)
		# 	if not i:
		# 		difference = float(attr[0]) - float(need_attr.title)
		# 		value = attr[0]
		# 		continue
		# 	if float(attr[0]) - float(need_attr.title) < difference:
		# 		difference = float(attr[0]) - float(need_attr.title)
		# 		value = attr[0]
		# 	print(value, difference)
		# return value
	
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
		# category = Category.objects.filter(title=self.product.category.title)
		# products2 = Product.objects.filter(category=self.product.category)#.values_list('manufacturer__title', named=True)
		# for pr in products2:
		# 	print(pr.manufacturer)
		# print(self.manufacturer_to.pk,self.manufacturer_to, self.product.category.pk, self.product.category.title, category, products2)
		self.products_found = Product.objects.filter(manufacturer=self.manufacturer_to, category__title=self.product.category.title)

		sft_attrs = self.product.attrs_vals.filter(attribute__type='sft')
		hrd_attrs = self.product.attrs_vals.filter(attribute__type='hrd')
		print(hrd_attrs, sft_attrs, self.products_found)
		for attr in hrd_attrs:
			self.products_found = self.products_found.filter(attrs_vals__title=attr.title, attrs_vals__attribute=attr.attribute)
			# print(attr.title, attr.attribute)
		if not self.products_found.count():
			print('Не найден ни один продукт по жестким атрибутам')
			pass # todo: make render with error | не найден продукт по жестким аттрибутам
		if self.products_found.count() == 1:
			pass # todo: make render response | успех
		else: # найдено более одного продукта по жестким
			middle_products_found = self.products_found

			for i, attr in enumerate(sft_attrs):
				test_middle_products = middle_products_found.filter(attrs_vals__title=attr.title, attrs_vals__attribute=attr.attribute)
				mdl_pr_count = test_middle_products.count()
				print('# SFT attr - ', mdl_pr_count)
				if mdl_pr_count:
					if mdl_pr_count > 1:
						if i + 1 == sft_attrs.count(): # check enf of cycle
							self.products_found = test_middle_products
							return self
						middle_products_found = test_middle_products
						#value = None
					else: # =1
						print('internal else, mdl_pr_count = ', mdl_pr_count)
						self.products_found = test_middle_products
						return self
				else:
					print('internal else, mdl_pr_count = ', mdl_pr_count, middle_products_found)
					first_need_attr = sft_attrs.order_by('attribute__priority')
					#print(first_need_attr, first_need_attr.attribute.title, first_need_attr.attribute.type)
					
					#  берём первый мягкий аттрибут согласно его приоритету у товара по которому ищем
					value = self.finding_the_сlosest_attribute_value(middle_products_found, attr)
					if i + 1 == sft_attrs.count():  # check enf of cycle
						self.products_found = middle_products_found.filter(attrs_vals__title=value,
						                                                   attrs_vals__attribute=attr.attribute)
					else:
						pass # todo: continue cycle
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
				return render(request, 'admin/catalog/search.html', {'Results': result.products_found[1:2], 'Product': result.product,
			                                                     'Error': error})
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