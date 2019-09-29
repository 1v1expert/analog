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
    def __init__(self, product=None, form=None, article=None):
        self.product = product
        self.form = form
        self.article = article
        
        if product is None:
            self.product = self._get_product()
        
    def _get_product(self):
        product = None
        if self.article is not None:
            product = Product.objects.get(article=self.article)
            
        if self.product is None and self.form is not None:
            product = self._get_product_from_form()
            
        return product
        
    def _get_product_from_form(self):
        article = self.form.cleaned_data.get('article')
        manufacturer_from = self.form.cleaned_data.get('manufacturer_from')
        
        if manufacturer_from:
            product = Product.objects.get(article=article, manufacturer=manufacturer_from)
        else:
            product = Product.objects.get(article=article)
        return product
    
    def _serialize_fix_attribute(self):
        fix_attributes = self.product.fixed_attrs_vals.all()
        return {'fix' + str(attr.pk): {'title': attr.attribute.title,
                                       'type_display': attr.attribute.get_type_display(),
                                       'choices': [(at.pk, at.title) for at in FixedValue.objects.filter(attribute=attr.attribute)],
                                       'type': attr.attribute.type
                                       } for attr in fix_attributes}
    
    def _serialize_unfix_attribute(self):
        unfix_attributes = self.product.unfixed_attrs_vals.all()
        return {
            'unfix' + str(attr.pk): {'title': attr.attribute.title,
                                     'type_display': attr.attribute.get_type_display(),
                                     'choices': TYPES_SEARCH,
                                     'type': attr.attribute.type
                                     } for attr in unfix_attributes}
    
    def get_attributes(self):
        attributes = {}
    
        attributes.update(self._serialize_fix_attribute())
        attributes.update(self._serialize_unfix_attribute())

        response = {'attributes': attributes, 'product_types': list((type_[0] for type_ in TYPES))[::-1],
                    'all_types': TYPES_DICT}
        return response
    
    def get_product_info(self):
        pass


def get_attributes(product, api=True):
    pass


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
