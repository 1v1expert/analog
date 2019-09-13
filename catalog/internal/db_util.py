from django.contrib.auth import models as auth_md

from catalog.models import Manufacturer, Product, FixedAttributeValue, UnFixedAttributeValue, Attribute

from catalog.internal.neural_network import NeuralNetworkOption2
from catalog import file_utils

import re


class ObjectHandling(object):
	
	@staticmethod
	def deleting_all_manufacturer_information(manufacturer):
		manufacturer_obj = manufacturer
		if isinstance(manufacturer, str):
			manufacturer_obj = Manufacturer.objects.get(title=manufacturer)
		
		products = Product.objects.filter(manufacturer=manufacturer_obj)
		for product in products:
			FixedAttributeValue.objects.filter(product=product).delete()
			UnFixedAttributeValue.objects.filter(product=product).delete()
		products.delete()
	
	@staticmethod
	def removal_of_all_unprocessed_products():
		Product.objects.filter(is_tried=False).delete()
		UnFixedAttributeValue.objects.filter(is_tried=False).delete()
		FixedAttributeValue.objects.filter(is_tried=False).delete()


def filling_in_categories_for_is_not_tried_products(products=None):
	if products is None:
		products = Product.objects.filter(is_tried=False)
	count, i = products.count(), 0
	for product in products:
		raw = product.raw
		i += 1
		if raw.get('category_from_neural_network'):
			continue
		
		network = NeuralNetworkOption2(loadmodel=True)
		name_category = network.predict(product.title, 1000)
		if not raw:
			raw = {}
		raw['category_from_neural_network'] = name_category
		product.raw = raw
		product.save()
		print('{} product processed from {}'.format(i, count))
		
		
def filling_attr_for_products(products=None):
	if products is None:
		products = Product.objects.filter(is_tried=False)
	print(products)
	
	user = auth_md.User.objects.get(is_staff=True, username='admin')
	
	for product in products:
		parameter = re.findall(r'(\d{,5})[х*x](\d{,5})[х*x](\d{,5})', product.title)
		print(product.title, parameter, len(parameter))
		if len(parameter) == 3:
			board_height = parameter[0]
			width = parameter[1]
			thickness = parameter[2]
			
			if file_utils.is_digit(board_height):
				try:
					product.fixed_attrs_vals.filter(attribute__title='высота борта')
				except FixedAttributeValue.DoesNotExist:
					attribute = Attribute.objects.get(title='высота борта')
					attr_val = FixedAttributeValue(value=float(board_height), attribute=attribute, created_by=user, updated_by=user)
					attr_val.save()
					attr_val.products.add(product)
					attr_val.save()
					product.fixed_attrs_vals.set(attr_val)
			
			if file_utils.is_digit(width):
				try:
					product.fixed_attrs_vals.filter(attribute__title='ширина')
				except FixedAttributeValue.DoesNotExist:
					attribute = Attribute.objects.get(title='ширина')
					attr_val = FixedAttributeValue(value=float(width), attribute=attribute, created_by=user, updated_by=user)
					attr_val.save()
					attr_val.products.add(product)
					attr_val.save()
					product.fixed_attrs_vals.set(attr_val)
					
			if file_utils.is_digit(thickness):
				try:
					product.fixed_attrs_vals.filter(attribute__title='толщина')
				except FixedAttributeValue.DoesNotExist:
					attribute = Attribute.objects.get(title='толщина')
					attr_val = FixedAttributeValue(value=float(thickness), attribute=attribute, created_by=user, updated_by=user)
					attr_val.save()
					attr_val.products.add(product)
					attr_val.save()
					product.fixed_attrs_vals.set(attr_val)