from collections import OrderedDict, defaultdict
import datetime

from catalog.models import Product, Attribute


class DefaultGeneratorTemplate(object):
	def __init__(self, manufacturer):
		self.manufacturer = manufacturer
		self.date = datetime.datetime.now()
	
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
		for seq, product in enumerate(Product.objects.filter(manufacturer=self.manufacturer)):
			yield OrderedDict([
				('seq', seq),
				('title', product.title),
				('article', product.article),
				('additional_article', product.additional_article),
				('series', product.series),
				('category', product.category.title)
			])
