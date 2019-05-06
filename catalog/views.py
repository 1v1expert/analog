from django.shortcuts import render, redirect, reverse
from .forms import *
from catalog.models import Product, AttributeValue, Category, DataFile
from catalog import choices
from catalog.handlers import handle_uploaded_search_file
from catalog.utils import SearchProducts


def render_search(request, queryset):
	return render(request, 'admin/catalog/search.html', queryset)
# Create your views here.


def result_processing(instance, request, product, default=True):
	instance.global_search(default=default)
	if instance.founded_products.count():
		if instance.founded_products.count() == 1:
			error = {'val': False}
		else:
			error = {'val': True, 'msg': 'Найдено более одного продукта, подходящего по параметрам поиска {}'}
		return render(request, 'admin/catalog/search.html',
		              {'Results': instance.founded_products, 'Product': product, 'Error': error})
	else:
		error = {'val': True, 'msg': 'Продукты, удовлетворяющие параметрам поиска, не найдены'}
		return render(request, 'admin/catalog/search.html',
		              {'Results': instance.founded_products, 'Product': product, 'Error': error})
	

def advanced_search_view(request, product_id, manufacturer_to, *args, **kwargs):
	print(manufacturer_to)
	product = Product.objects.get(pk=product_id)
	attributes = product.category.attributes.all()#.exclude(type='hrd')
	#attributes = product.attrs_vals.all()
	attributes_array = {str(attr.pk): {'title': attr.title,
	                                   'type_display': attr.get_type_display(),
	                                   'type': attr.type} for attr in attributes}
	# print(attributes_array)
	# print(attributes_array)
	# attributes_list = [(attr.title, attr.get_type_display(), attr.pk, attr.type) for attr in attributes]
	# print(attributes_list)
	data = {'article': product.article}
	advanced_form = AdvancedSearchForm(extra=attributes_array, initial=data)
	# manufacturer_from
	if request.method == 'POST':
		advanced_form = AdvancedSearchForm(request.POST, extra=attributes_array)
		if advanced_form.is_valid():
			advanced_form.cleaned_data['manufacturer_from'] = product.manufacturer
			advanced_form.cleaned_data['manufacturer_to'] = manufacturer_to
			#print(advanced_form.cleaned_data)
			result = SearchProducts(request, advanced_form, product)
			return result_processing(result, request, product, default=False)
			
	#advanced_form.article = product.article
	# form = SearchForm(request.POST)
	# print(form.is_valid())
	# if form.is_valid():
	# 	advanced_search = form.cleaned_data['advanced_search']
	# 	article = form.cleaned_data['article']
	# 	manufacturer_from = form.cleaned_data['manufacturer_from']
	# product = Product.objects.get(article=article, manufacturer=manufacturer_from)
	# attributes = product.category.attributes.all()
	# attributes_list = [(attr.title, attr.type) for attr in attributes]
	# advanced_form = AdvancedSearchForm(request.POST, extra=attributes_list)
	return render(request, 'admin/catalog/advanced_search.html', {'advanced_form': advanced_form, 'product': product,
	                                                              'manufacturer_to': manufacturer_to})#, {'advanced_form': advanced_form})

	
def search_view(request):
	form = SearchForm()
	if request.method == 'POST':
		form = SearchForm(request.POST)
		if form.is_valid():
			advanced_search = form.cleaned_data['advanced_search']
			article = form.cleaned_data['article']
			manufacturer_from = form.cleaned_data['manufacturer_from']
			manufacturer_to = form.cleaned_data['manufacturer_to']
			
			try:
				product = Product.objects.get(article=article, manufacturer=manufacturer_from)
			except Product.DoesNotExist:
				return render(request, 'admin/catalog/search.html',
				              {'Error': {'val': True, 'msg': 'Не найден продукт с артикулом {}'.format(article)}})
			except Product.MultipleObjectsReturned:
				return render(request, 'admin/catalog/search.html',
				              {'Error': {'val': True, 'msg': 'Найдено более одного продукта с артикулом {}'
				                                             'и производителем {}'.format(article, manufacturer_from)}})
			
			if advanced_search:
				return redirect('catalog:advanced_search', product.pk, manufacturer_to.id)
			else:
				result = SearchProducts(request, form, product)
				return result_processing(result, request, product, default=True)
				# return SearchProducts(request, form, product).search()

		return render(request, 'admin/catalog/search.html', {'Error': 'Ошибка формы'})

	return render(request, 'admin/catalog/search.html', {'form': form})


def search_from_file_view(request):
	if request.method == 'POST':
		form = SearchFromFile(request.POST, request.FILES)
		print(vars(form), form.is_valid())
		if form.is_valid():
			print(form.is_valid())
			instance = DataFile(file=request.FILES['file'], type=choices.TYPES_FILE[1])
			instance.save()
			print(vars(instance))
			return handle_uploaded_search_file(request.FILES['file'], instance.file.path)
	else:
		form = SearchFromFile()
	return render(request, 'admin/catalog/search.html', {'file_form': form})