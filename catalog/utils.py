from django.shortcuts import render
from catalog.models import Product


class SearchProducts(object):
	def __init__(self, request, form, product):

		self.request = request
		self.manufacturer_from = form.cleaned_data['manufacturer_from']
		self.manufacturer_to = form.cleaned_data['manufacturer_to']
		self.article = form.cleaned_data['article']
		self.product = product
		self.products_found = None
	
	@staticmethod
	def finding_the_closest_attribute_value(all_attr, step_attr):
		# first_attr = need_attr.first()
		# print(need_attr, need_attr)
		# # all_attrr = all_attr.filter(attrs_vals__attribute__title=first_attr[1]) # title
		# print(need_attr, '\n\n', all_attr, '\n\n', step_attr.title)
		# difference = None
		# value = None
		values_list = [
			float(attr.attrs_vals.get(attribute__type='sft', attribute__title=step_attr.attribute.title).title) for attr
			in all_attr]
		value = min(values_list, key=lambda x: abs(x - float(step_attr.title)))
		print(values_list, )
		return value
	
	def search(self, *args):
		print(args)
		
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
