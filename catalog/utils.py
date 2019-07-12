from django.shortcuts import render

from catalog.models import Product, UnFixedAttributeValue
import time
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
		self.start_time = time.time()
		self.lead_time = 0
	
	@staticmethod
	def finding_the_closest_attribute_value(all_attr, step_attr, method, types='sft'):
		# values_list = [
		# 	attr.unfixed_attrs_vals.get(attribute__type=types, attribute__title=step_attr.attribute.title).value for attr
		# 	in all_attr]
		
		values_list = []
		for attr in all_attr:
			try:
				value = attr.unfixed_attrs_vals.get(attribute__type=types, attribute__title=step_attr.attribute.title).value
			except UnFixedAttributeValue.DoesNotExist:
				value = 0
			values_list.append(value)
		
		# print(values_list)
		
		if method == 'min':
			value = min(values_list, key=lambda x: x)
		elif method == 'max':
			value = max(values_list, key=lambda x: x)
		else:   # method = 'nearest
			value = min(values_list, key=lambda x: abs(x - step_attr.value))
		return value
	
	def smart_attribute_search(self, default=True):
		method = 'nearest'
		all_fix_attributes = self.product.fixed_attrs_vals.all()
		all_unfix_attributes = self.product.unfixed_attrs_vals.all()
		# hrd attr
		hrd = 'hrd'
		hrd_fix_attributes = all_fix_attributes.filter(attribute__type=hrd)#self.product.fixed_attrs_vals.filter(attribute__type=hrd)
		# print(hrd_fix_attributes)
		hrd_unfix_attributes = all_unfix_attributes.filter(attribute__type=hrd)#self.product.unfixed_attrs_vals.filter(attribute__type=hrd)
		for hrd_fix_attr in hrd_fix_attributes:
			# print('HRD_FIX_ATTR', hrd_fix_attr.value.title)
			if default:
				value = hrd_fix_attr.value.pk
			else:
				value = self.form.cleaned_data['extra_field_fix{}'.format(hrd_fix_attr.pk)]
			# print(value)
			self.founded_products = self.founded_products.filter(fixed_attrs_vals__value__pk=value,#attrs_vals__title=attribute.title,
			                                                     fixed_attrs_vals__attribute=hrd_fix_attr.attribute)
		# print('Count after HRD FIX search prdcts-> ', self.founded_products.count())
		for hrd_unfix_attr in hrd_unfix_attributes:
			if not default:
				method = self.form.cleaned_data['extra_field_unfix{}'.format(hrd_unfix_attr.pk)]
			value = self.finding_the_closest_attribute_value(self.founded_products, hrd_unfix_attr, method, types=hrd)
			# print(value, hrd_unfix_attr.value, type(value), type(hrd_unfix_attr.value))
			self.founded_products = self.founded_products.filter(unfixed_attrs_vals__value=value,#attrs_vals__title=attribute.title,
			                                                     unfixed_attrs_vals__attribute=hrd_unfix_attr.attribute)
																#attrs_vals__attribute=attribute.attribute)
		
		# print('Count after HRD search prdcts-> ', self.founded_products.count())
		if not self.founded_products.exists():
			return
		# middle_results = self.founded_products
		# sft attr
		sft = 'sft'
		sft_fix_attributes = all_fix_attributes.filter(attribute__type=sft)#self.product.fixed_attrs_vals.filter(attribute__type=sft)
		# print(sft_fix_attributes)
		sft_unfix_attributes = all_unfix_attributes.filter(attribute__type=sft)#self.product.unfixed_attrs_vals.filter(attribute__type=sft)
		for sft_fix_attr in sft_fix_attributes:
			if default:
				value = sft_fix_attr.value.pk
			else:
				value = self.form.cleaned_data['extra_field_fix{}'.format(sft_fix_attr.pk)]
			# print(value)
			middle_results = self.founded_products.filter(fixed_attrs_vals__value__pk=value,
			                                                     # attrs_vals__title=attribute.title,
			                                                     fixed_attrs_vals__attribute=sft_fix_attr.attribute)
			count = middle_results.count()
			if count > 1:
				self.founded_products = middle_results
			if count == 1:
				self.founded_products = middle_results
				return
		# print('Count after SFT FIX search prdcts-> ', self.founded_products.count())
		# middle_results = self.founded_products
		for sft_unfix_attr in sft_unfix_attributes:
			if not default:
				method = self.form.cleaned_data['extra_field_unfix{}'.format(sft_unfix_attr.pk)]
			value = self.finding_the_closest_attribute_value(self.founded_products, sft_unfix_attr, method, types=sft)
			# print(value, sft_unfix_attr.value, type(value), type(sft_unfix_attr.value))
			middle_results = self.founded_products.filter(unfixed_attrs_vals__value=value,
			                                                     # attrs_vals__title=attribute.title,
			                                                     unfixed_attrs_vals__attribute=sft_unfix_attr.attribute)
			count = middle_results.count()
			if count > 1:
				self.founded_products = middle_results
			if count == 1:
				self.founded_products = middle_results
				return
			
		# rcl attr
		rcl = 'rcl'
		rcl_unfix_attributes = all_unfix_attributes.filter(attribute__type=rcl)#self.product.unfixed_attrs_vals.filter(attribute__type=rcl)
		# print(rcl_unfix_attributes)
		# print('Count after SFT search prdcts-> ', self.founded_products.count())
		# middle_results = self.founded_products
		for rcl_unfix_attr in rcl_unfix_attributes:
			if not default:
				method = self.form.cleaned_data['extra_field_unfix{}'.format(rcl_unfix_attr.pk)]
			value = self.finding_the_closest_attribute_value(self.founded_products, rcl_unfix_attr, method, types=rcl)
			# print(value, rcl_unfix_attr.value, type(value), type(rcl_unfix_attr.value))
			middle_results = self.founded_products.filter(unfixed_attrs_vals__value=value,
			                                              # attrs_vals__title=attribute.title,
			                                              unfixed_attrs_vals__attribute=rcl_unfix_attr.attribute)
			count = middle_results.count()
			if count > 1:
				self.founded_products = middle_results
			if count == 1:
				self.founded_products = middle_results
				return
		# ==============================================================================
		# middle_results = founded_products
		# method = 'nearest'
		# # print('count products - ', self.founded_products.count())
		# for type_attr in TYPES:  # (hrd, sft, rcl, rlt, prc)
		# 	fix_attributes = self.product.fixed_attrs_vals.filter(attribute__type=type_attr[0])
		# 	unfix_attributes = self.product.unfixed_attrs_vals.filter(attribute__type=type_attr[0])
		# 	attributes = self.product.attrs_vals.filter(attribute__type=type_attr[0])
		# 	# print(attributes)
		# 	if attributes.count():  # если аттрибуты этого типа есть у искомого продукта
		# 		for attribute in attributes:
		# 			if not default:
		# 				# print(self.form.cleaned_data)
		# 				method = self.form.cleaned_data['extra_field_{}'.format(attribute.attribute.pk)]
		# 			# print('Attribute id ->', attribute.attribute.pk, method)
		# 			if type_attr[0] in ('hrd'):
		#
		# 					try:  # check float or string value attribute
		# 						float(attribute.title)
		# 						# print('float attribute value {}, type {}'.format(attribute.title, type_attr[0]))
		# 						value = self.finding_the_closest_attribute_value(self.founded_products,
		# 						                                                 attribute,
		# 						                                                 method,
		# 						                                                 types=type_attr[0])
		# 						self.founded_products = self.founded_products.filter(attrs_vals__title=value,
		# 						                                       attrs_vals__attribute=attribute.attribute)
		# 						# print('count products - ', self.founded_products.count())
		# 					except ValueError:
		# 						# print('fixed attribute value {}, type {}'.format(attribute.title, type_attr[0]))
		# 						self.founded_products = self.founded_products.filter(attrs_vals__title=attribute.title,
		# 					                                            attrs_vals__attribute=attribute.attribute)
		# 						# print('count products - ', self.founded_products.count())
		# 			else:  # another types (sft, rcl, rlt, prc)
		#
		# 				# print('another attributes - ', type_attr[0], '; count results - ', self.founded_products.count())
		# 				middle_results = self.founded_products
		# 				if middle_results.count():
		# 					if middle_results.count() == 1:
		# 						self.founded_products = middle_results
		# 						break
		# 					else:
		#
		# 						try:  # check float or string value attribute
		# 							float(attribute.title)
		# 							# print('float attribute value {}, type {}'.format(attribute.title, type_attr[0]))
		# 							value = self.finding_the_closest_attribute_value(middle_results,
		# 							                                                 attribute,
		# 							                                                 method,
		# 							                                                 types=type_attr[0])
		# 							middle_results = middle_results.filter(attrs_vals__title=value,
		# 							                                                     attrs_vals__attribute=attribute.attribute)
		# 							# print('middle counts result after filter - ', middle_results.count())
		# 						except ValueError:
		# 							# print('fixed attribute value {}, type {}'.format(attribute.title, type_attr[0]))
		# 							middle_results = middle_results.filter(attrs_vals__title=attribute.title,
		# 							                                                     attrs_vals__attribute=attribute.attribute)
		# 							# print('middle counts result after filter - ', middle_results.count())
		# 						if middle_results.count():
		# 							self.founded_products = middle_results
		# 				else:
		# 					self.founded_products = middle_results
	
	# def advanced_search_for_attributes(self, founded_products, **kwargs):
	# 	print(kwargs)
	# 	print(self.form.cleaned_data)
	# 	self.default_search_for_attributes(founded_products)
	# 	return self
	
	def global_search(self, default=True):
		
		self.founded_products = Product.objects.filter(manufacturer=self.manufacturer_to, category=self.product.category)
		if self.founded_products.exists():
			# print('Count fnd prdcts-> ', self.founded_products.count())
			self.smart_attribute_search(default=default)
		self.lead_time = time.time() - self.start_time
		# print('Count after search prdcts-> ', self.founded_products.count())
		# print("--- %s seconds ---" % (time.time() - start_time))
		#print('FOUNDED PRODUCTS', self.founded_products.first().article, 'Count-> ', self.founded_products.count())
