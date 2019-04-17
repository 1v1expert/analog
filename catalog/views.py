from django.shortcuts import render
from .forms import *
from .models import Product, AttributeValue

# Create your views here.

def search_view(request):
	form = SearchForm()
	advanced_form = AdvancedeSearchForm()
	
	if request.method == 'POST':
		form = SearchForm(request.POST)
		if form.is_valid():
			try:
				product = Product.objects.get(article=form.cleaned_data['article'], manufacturer=form.cleaned_data['manufacturer_from'])
				products_values = AttributeValue.objects.filter(product=product)
				find_products = Product.objects.filter(manufacturer=form.cleaned_data['manufacturer_to'], category=product.category)
				for attr in products_values:
					# find_product = find_product.filter(attrs_vals__attribute=attr.attribute,
					#                                    attrs_vals__title=attr.title)
					if attr.attribute.type == 'hrd':
						# print(find_product)
						find_products = find_products.filter(attrs_vals__attribute=attr.attribute, attrs_vals__title=attr.title)
						# print('hrd', attr)
				if find_products.count() == 1:
					error = {'val': False}
				elif find_products.count() == 0:
					error = {'val': True, 'msg': 'По заданным параметрам не найдено продуктов'}
				else:
					error = {'val': True, 'msg': 'По заданным параметрам найдено более одного продукта'}
				return render(request, 'admin/catalog/search.html', {'Results': find_products,
				                                                     'Error': error})
				# print(products_values, find_product)
				#print(product.category)
				#print(product.category.attributes.filter(type='hrd'))
				#find_product = Product.objects.filter(manufacturer=form.cleaned_data['manufacturer_to'])
				#print(find_product)
			except:
				return render(request, 'admin/catalog/search.html', {'Error': {'val': True, 'msg': 'Произошла ошибка при поиске артикула {}'.format(form.cleaned_data['article'])}})
				
			
			#print(form.cleaned_data)
		return render(request, 'admin/catalog/search.html', {'Fake': 'Fake'})

	return render(request, 'admin/catalog/search.html', {'form': form, 'advanced_form': advanced_form}) #{'form': form})