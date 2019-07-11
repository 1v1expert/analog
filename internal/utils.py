from catalog.models import FixedValue
from catalog.choices import TYPES_SEARCH, TYPES_DICT, TYPES


def get_attributes(product, api=True):
	fix_attributes = product.fixed_attrs_vals.all()  # category.attributes.all()
	unfix_attributes = product.unfixed_attrs_vals.all()  # category.attributes.all()
	attributes_array = {
		'fix' + str(attr.pk): {'title': attr.attribute.title, 'type_display': attr.attribute.get_type_display(),
		                       'choices': [(at.pk, at.title) for at in
		                                   FixedValue.objects.filter(attribute=attr.attribute)]
		                       # serializers.serialize('json',
		                       #                             FixedValue.objects.filter(attribute=attr.attribute),
		                       #                             fields=('pk', 'title'))
		                       # .values_list('pk', 'title'))
			,  # 'choices': [attribute.title for attribute in FixedValue.objects.filter(attribute=attr.attribute)],
			                   'type': attr.attribute.type} for attr in fix_attributes}
	unfix_attributes_array = {
		'unfix' + str(attr.pk): {'title': attr.attribute.title, 'type_display': attr.attribute.get_type_display(),
		                         'choices': TYPES_SEARCH, 'type': attr.attribute.type} for attr in unfix_attributes}
	
	attributes_array.update(unfix_attributes_array)
	
	# types = set(product.category.attributes.all().values_list('type',  flat=True))
	response = {'attributes': attributes_array, 'product_types': list((type_[0] for type_ in TYPES))[::-1],
	            'all_types': TYPES_DICT}
	return response


def get_product_info(product):
	fix_attributes = product.fixed_attrs_vals.all()  # category.attributes.all()
	unfix_attributes = product.unfixed_attrs_vals.all()  # category.attributes.all()
	
	info = [{attr.attribute.title: attr.value} for attr in unfix_attributes]
	for attr in fix_attributes:
		info.append({attr.attribute.title: attr.value.title})
	
	return info
