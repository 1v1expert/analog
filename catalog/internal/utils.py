from catalog.models import FixedValue, Product
from catalog.choices import TYPES_SEARCH, TYPES_DICT, TYPES


class DuplicateCheck(object):
    
    def __init__(self, product=None):
        if not product:
            self.global_search()
        
        self._product = product
    
    # self.search_duplicates()
    
    @staticmethod
    def global_search():
        products = Product.objects.all()
        for product in products:
            product.refresh_from_db()
            
            if product.is_duplicate:
                continue
            
            selection = Product.objects.filter(article=product.article)
            if selection.count() > 1:
                selection.update(is_duplicate=True)
    
    @staticmethod
    def get_products(article: str):
        return Product.objects.filter(article=article)
    
    def search_duplicates(self, api=False):
        if isinstance(self._product, str):
            products = self.get_products(self._product)
            if not products.exists():
                raise Exception('Not found product with article {}'.format(self._product))
            
            if api:
                return products.values_list('article')
            return products
    
    # return list()
    
    # str product articule


class ProductInfo(object):
    def __init__(self, product):
        self.product = product
    
    def get_attributes(self):
        pass
    
    def get_product_info(self):
        pass


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
    info = []
    info.append({"наименование": product.title})
    
    fix_attributes = product.fixed_attrs_vals \
        .all() \
        .exclude(attribute__title='ед.изм') \
        .select_related('value', 'attribute')  # category.attributes.all()
    unfix_attributes = product.unfixed_attrs_vals \
        .all() \
        .exclude(attribute__title='цена') \
        .select_related('attribute')  # category.attributes.all()
    
    # additional_info = [{attr.attribute.title: attr.value} for attr in ]
    for attr in unfix_attributes:
        info.append({attr.attribute.title: attr.value})
    
    for attr in fix_attributes:
        info.append({attr.attribute.title: attr.value.title})
    
    info.append({"производитель": product.manufacturer.title})
    
    return info
