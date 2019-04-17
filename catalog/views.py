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
				find_product = Product.objects.filter(manufacturer=form.cleaned_data['manufacturer_to'])
				for attr in products_values:
					if attr.attribute.type=='hrd':
						find_product = find_product.filter(attrs_vals_=attr)
						print('hrd', attr)
					
				print(products_values, find_product)
				#print(product.category)
				#print(product.category.attributes.filter(type='hrd'))
				#find_product = Product.objects.filter(manufacturer=form.cleaned_data['manufacturer_to'])
				#print(find_product)
			except:
				return render(request, 'admin/catalog/search.html', {'Error': {'val': True, 'msg': 'Произошла ошибка при поиске артикула {}'.format(form.cleaned_data['article'])}})
				
			
			#print(form.cleaned_data)
		return render(request, 'admin/catalog/search.html', {'Fake': 'Fake'})

	return render(request, 'admin/catalog/search.html', {'form': form, 'advanced_form': advanced_form}) #{'form': form})