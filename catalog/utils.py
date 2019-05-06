from django.shortcuts import render

from catalog.models import Product
from catalog.choices import TYPES


class SearchProducts(object):
	def __init__(self, request, form, product):

		self.request = request
		self.form = form
		self.manufacturer_from = form.cleaned_data['manufacturer_from']
		self.manufacturer_to = form.cleaned_data['manufacturer_to']
		self.article = form.cleaned_data['article']
		self.product = product
		self.products_found = None
		self.founded_products = None
	
	@staticmethod
	def finding_the_closest_attribute_value(all_attr, step_attr, method, types='sft'):
		# print('Into finding float values')
		# first_attr = need_attr.first()
		# print(need_attr, need_attr)
		# # all_attrr = all_attr.filter(attrs_vals__attribute__title=first_attr[1]) # title
		# print(need_attr, '\n\n', all_attr, '\n\n', step_attr.title)
		# difference = None
		# value = None
		values_list = [
			attr.attrs_vals.get(attribute__type=types, attribute__title=step_attr.attribute.title).title for attr
			in all_attr]
		
		if method == 'min':
			value = min(values_list, key=lambda x: float(x))
		elif method == 'max':
			value = max(values_list, key=lambda x: float(x))
		else:   # method = 'nearest
			value = min(values_list, key=lambda x: abs(float(x) - float(step_attr.title)))
		return value
	
	def smart_attribute_search(self, founded_products, default=True):
		# middle_results = founded_products
		method = 'nearest'
		# print('count products - ', self.founded_products.count())
		for type_attr in TYPES:  # (hrd, sft, rcl, rlt, prc)
			attributes = self.product.attrs_vals.filter(attribute__type=type_attr[0])
			# print(attributes)
			if attributes.count():  # если аттрибуты этого типа есть у искомого продукта
				for attribute in attributes:
					if not default:
						# print(self.form.cleaned_data)
						method = self.form.cleaned_data['extra_field_{}'.format(attribute.attribute.pk)]
					# print('Attribute id ->', attribute.attribute.pk, method)
					if type_attr[0] in ('hrd'):
							
							try:  # check float or string value attribute
								float(attribute.title)
								# print('float attribute value {}, type {}'.format(attribute.title, type_attr[0]))
								value = self.finding_the_closest_attribute_value(self.founded_products,
								                                                 attribute,
								                                                 method,
								                                                 types=type_attr[0])
								self.founded_products = self.founded_products.filter(attrs_vals__title=value,
								                                       attrs_vals__attribute=attribute.attribute)
								# print('count products - ', self.founded_products.count())
							except ValueError:
								# print('fixed attribute value {}, type {}'.format(attribute.title, type_attr[0]))
								self.founded_products = self.founded_products.filter(attrs_vals__title=attribute.title,
							                                            attrs_vals__attribute=attribute.attribute)
								# print('count products - ', self.founded_products.count())
					else:  # another types (sft, rcl, rlt, prc)
						
						# print('another attributes - ', type_attr[0], '; count results - ', self.founded_products.count())
						middle_results = self.founded_products
						if middle_results.count():
							if middle_results.count() == 1:
								self.founded_products = middle_results
								break
							else:
								
								try:  # check float or string value attribute
									float(attribute.title)
									# print('float attribute value {}, type {}'.format(attribute.title, type_attr[0]))
									value = self.finding_the_closest_attribute_value(middle_results,
									                                                 attribute,
									                                                 method,
									                                                 types=type_attr[0])
									middle_results = middle_results.filter(attrs_vals__title=value,
									                                                     attrs_vals__attribute=attribute.attribute)
									# print('middle counts result after filter - ', middle_results.count())
								except ValueError:
									# print('fixed attribute value {}, type {}'.format(attribute.title, type_attr[0]))
									middle_results = middle_results.filter(attrs_vals__title=attribute.title,
									                                                     attrs_vals__attribute=attribute.attribute)
									# print('middle counts result after filter - ', middle_results.count())
								if middle_results.count():
									self.founded_products = middle_results
						else:
							self.founded_products = middle_results
	
	# def advanced_search_for_attributes(self, founded_products, **kwargs):
	# 	print(kwargs)
	# 	print(self.form.cleaned_data)
	# 	self.default_search_for_attributes(founded_products)
	# 	return self
	
	def global_search(self, default=True):
		self.founded_products = Product.objects.filter(manufacturer=self.manufacturer_to, category=self.product.category)
		self.smart_attribute_search(self.founded_products, default=default)
		print('FOUNDED PRODUCTS', self.founded_products.first().article)
		# print('bool - ', bool(kwargs))
		# if not kwargs:  # default search
		# 	self.default_search_for_attributes(self.founded_products)
		# 	print('FOUNDED PRODUCTS', self.founded_products.first().article)
		# 	return self
		# else:
		# 	self.advanced_search_for_attributes(self.founded_products, **kwargs)  # this should be un default search
		
		# self.founded_products = founded_products
		# return self
			#print(type_attr, *args)
	
	def search(self, **kwargs):
		print(kwargs)
		# print(args, bool(args))
		
		# print(value, difference, '\n\n', all_attr)
		# try:
		# 	self.product = Product.objects.get(article=self.article, manufacturer=self.manufacturer_from)
		# except Product.DoesNotExist:
		# 	return render(self.request, 'admin/catalog/search.html',
		# 	              {'Error': {'val': True, 'msg': 'Не найден продукт с артикулом {}'.format(self.article)}})
		# except Product.MultipleObjectsReturned:
		# 	return render(self.request, 'admin/catalog/search.html',
		# 	              {'Error': {'val': True, 'msg': 'Найдено более одного продукта с артикулом {}'
		# 	                                             'и производителем {}'.format(self.article,
		# 	                                                                          self.manufacturer_from)}})
		# initial filter product
		# category = Category.objects.filter(title=self.product.category.title)
		# products2 = Product.objects.filter(category=self.product.category)#.values_list('manufacturer__title', named=True)
		# for pr in products2:
		# 	print(pr.manufacturer)
		# print(self.manufacturer_to.pk,self.manufacturer_to, self.product.category.pk, self.product.category.title, category, products2)
		self.products_found = Product.objects.filter(manufacturer=self.manufacturer_to, category=self.product.category)
		# , category__title=self.product.category.title)
		
		sft_attrs = self.product.attrs_vals.filter(attribute__type='sft')
		hrd_attrs = self.product.attrs_vals.filter(attribute__type='hrd')
		print(hrd_attrs, sft_attrs, self.products_found)
		for attr in hrd_attrs:
			self.products_found = self.products_found.filter(attrs_vals__title=attr.title,
			                                                 attrs_vals__attribute=attr.attribute)
		# print(attr.title, attr.attribute)
		if not self.products_found.count():
			print('Не найден ни один продукт по жестким атрибутам')
			pass  # todo: make render with error | не найден продукт по жестким аттрибутам
		if self.products_found.count() == 1:
			pass  # todo: make render response | успех
		else:  # найдено более одного продукта по жестким
			middle_products_found = self.products_found
			
			for i, attr in enumerate(sft_attrs):
				test_middle_products = middle_products_found.filter(attrs_vals__title=attr.title,
				                                                    attrs_vals__attribute=attr.attribute)
				mdl_pr_count = test_middle_products.count()
				print('# SFT attr - ', mdl_pr_count)
				if mdl_pr_count:
					if mdl_pr_count > 1:
						if i + 1 == sft_attrs.count():  # check enf of cycle
							self.products_found = test_middle_products[1:2]
							# return self
							return render(self.request, 'admin/catalog/search.html',
							              {'Results': self.products_found, 'Product': self.product, 'Error': {}})
						middle_products_found = test_middle_products
					# value = None
					else:  # =1
						print('internal else, mdl_pr_count = ', mdl_pr_count)
						self.products_found = test_middle_products
						# return self
						return render(self.request, 'admin/catalog/search.html',
						              {'Results': self.products_found, 'Product': self.product, 'Error': {}})
				
				else:
					print('internal else, mdl_pr_count = ', mdl_pr_count, middle_products_found)
					first_need_attr = sft_attrs.order_by('attribute__priority')
					# print(first_need_attr, first_need_attr.attribute.title, first_need_attr.attribute.type)
					
					#  берём первый мягкий аттрибут согласно его приоритету у товара по которому ищем
					value = self.finding_the_closest_attribute_value(middle_products_found, attr)
					if i + 1 == sft_attrs.count():  # check enf of cycle
						self.products_found = middle_products_found.filter(attrs_vals__title=value,
						                                                   attrs_vals__attribute=attr.attribute)
					else:
						pass  # todo: continue cycle
		return render(self.request, 'admin/catalog/search.html',
		              {'Results': self.products_found, 'Product': self.product, 'Error': {}})  #  self
