from catalog.models import Manufacturer, Product, FixedAttributeValue, UnFixedAttributeValue


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
