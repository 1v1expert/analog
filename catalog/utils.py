from django.shortcuts import render

from catalog.models import Product
from catalog.choices import TYPES


class SearchProducts(object):
	def __init__(self, request, form, product):

		self.request = request
		self.form = form
		self.manufacturer_from = form.cleaned_data['manufacturer_from']
		self.manufacturer_to = form.cleaned_data['manufacturer_to']
		# self.article = form.cleaned_data['article']
		self.product = product
		self.founded_products = None
	
	@staticmethod
	def finding_the_closest_attribute_value(all_attr, step_attr, method, types='sft'):
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
	
	def smart_attribute_search(self, default=True):
		# middle_results = founded_products
		method = 'nearest'
		# print('count products - ', self.founded_products.count())
		for type_attr in TYPES:  # (hrd, sft, rcl, rlt, prc)
			fix_attributes = self.product.fixed_attrs_vals.filter(attribute__type=type_attr[0])
			unfix_attributes = self.product.unfixed_attrs_vals.filter(attribute__type=type_attr[0])
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
		self.smart_attribute_search(default=default)
		print('FOUNDED PRODUCTS', self.founded_products.first().article, 'Count-> ', self.founded_products.count())
