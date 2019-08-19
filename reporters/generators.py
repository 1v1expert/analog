from collections import OrderedDict, defaultdict
import datetime

from catalog.models import Product, Attribute, FixedAttributeValue, UnFixedAttributeValue


class DefaultGeneratorTemplate(object):
	def __init__(self, manufacturer):
		self.manufacturer = manufacturer
		self.date = datetime.datetime.now()
		self.attributes = Attribute.objects.values_list('title', flat=True)
	
	def generate(self):
		data = {
			"top_header": {
				'spread': None,
				'row': []
			},
			"table_header": OrderedDict([
				                            ('seq', '№ п/п'),
				                            ('title', 'Наименование'),
				                            ('article', 'Артикул'),
				                            ('additional_article', 'Доп. артикул'),
				                            ('series', 'Серия'),
				                            ('category', 'Категория')
			                            ] + list(Attribute.objects.values_list('id', 'title'))
			                            ),
			"table_data": self.do_products()
		}
		data["top_header"]["spread"] = len(data['table_header'])
		
		return data
	
	def do_products(self):
		for seq, product in enumerate(
				Product.objects.filter(manufacturer=self.manufacturer).prefetch_related('fixed_attrs_vals',
				                                                                        'fixed_attrs_vals__value',
				                                                                        'fixed_attrs_vals__attribute',
				                                                                        'unfixed_attrs_vals',
				                                                                        'unfixed_attrs_vals__attribute')
		):
			yield OrderedDict([
				('seq', seq),
				('title', product.title),
				('article', product.article),
				('additional_article', product.additional_article),
				('series', product.series),
				('category', product.category.title)
			] + self._get_attributes(product))
	
	def _get_attributes(self, product):
		list_attributes = []
		fixed_attr_vals = product.fixed_attrs_vals.all()
		unfixed_attr_vals = product.unfixed_attrs_vals.all()
		
		for i, attribute in enumerate(self.attributes):
			is_found = False
			for fix in fixed_attr_vals:
				if attribute in fix.attribute.title:
					list_attributes.append((i, fix.value.title))
					is_found = True
					break
					
			if is_found: continue
			
			for unfix in unfixed_attr_vals:
				if attribute in unfix.attribute.title:
					list_attributes.append((i, str(unfix.value)))
					is_found = True
					break
			
			if not is_found:
				list_attributes.append((i, ''))
		
		return list_attributes
		
		
		
		# list_attribute = []
		# for attribute in Attribute.objects.all():
		# 	list_attribute.append((attribute.id, self._get_attribute(product, attribute)))
		# return list_attribute
	
	# @staticmethod
	# def _get_attribute(product, attribute):
	# 	def _get_unfix():
	# 		try:
	# 			return UnFixedAttributeValue.objects.get(product=product, attribute=attribute)
	# 		except (UnFixedAttributeValue.DoesNotExist, UnFixedAttributeValue.MultipleObjectsReturned):
	# 			return None
	#
	# 	def _get_fix():
	# 		try:
	# 			return FixedAttributeValue.objects.get(product=product, attribute=attribute)
	# 		except (FixedAttributeValue.DoesNotExist, FixedAttributeValue.MultipleObjectsReturned):
	# 			return None
	#
	# 	value_fix = _get_fix()
	# 	if value_fix is not None:
	# 		return value_fix.value.title
	# 	value_unfix = _get_unfix()
	# 	if value_unfix is not None:
	# 		return value_unfix.value
	# 	return ''

