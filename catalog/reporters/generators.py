from collections import OrderedDict, defaultdict
import datetime

from catalog.models import Product, Attribute


class DefaultGeneratorTemplate(object):
    """Стандартный генератор по производителям"""
    def __init__(self, manufactures=None):
        self.manufactures = manufactures
        # self.products = products
        self.date = datetime.datetime.now()
        self.attributes = Attribute.objects.values_list('title', flat=True)
    
    def _get_data(self, manufacturer=None, name_sheet=None, products=None) -> dict:
        data = {
            "top_header": {
                'spread': None,
                'row': [],
                'name': name_sheet if name_sheet else str(manufacturer)
            },
            "table_header": OrderedDict([
                                            ('seq', '№ п/п'),
                                            ('title', 'Наименование'),
                                            ('article', 'Артикул'),
                                            ('additional_article', 'Доп. артикул'),
                                            ('series', 'Серия'),
                                            ('category', 'Категория'),
                                        ] + list(Attribute.objects.values_list('id', 'title'))
                                        ),
            "table_data": self.do_products(manufacturer=manufacturer, products=products)
        }
        data["top_header"]["spread"] = len(data['table_header'])
    
        return data
    
    def generate(self) -> dict:
        for manufacturer in self.manufactures:
            yield self._get_data(manufacturer)
            
    def do_products(self, manufacturer=None, products=None) -> OrderedDict:
        if products is None:
            products = Product.objects.filter(manufacturer=manufacturer) \
                .prefetch_related(
                'fixed_attrs_vals',
                'fixed_attrs_vals__value',
                'fixed_attrs_vals__attribute',
                'unfixed_attrs_vals',
                'unfixed_attrs_vals__attribute'
            )

        for seq, product in enumerate(products):
                yield OrderedDict([
                                      ('seq', seq),
                                      ('title', product.title),
                                      ('manufacturer', product.manufacturer.title),
                                      ('article', product.article),
                                      ('additional_article', product.additional_article),
                                      ('series', product.series),
                                      ('category', product.category.title),
                                  ] + self._get_attributes(product))
    
    def _get_attributes(self, product) -> list:
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


class AdditionalGeneratorTemplate(object):
    """Генератор отчётов по инстансам базовых классов с произвольным фильтром"""
    
    def __init__(self, classes, *args, **kwargs):
        self.classes = classes
        self.local_fields = None
        self.kwargs = kwargs
        
    def _get_data(self, cls_obj):
        data = {
            "top_header": {
                'spread': None,
                'row': [],
                'name': str(cls_obj._meta.verbose_name),
            },
            "table_header": OrderedDict([(field.name, field.verbose_name) for field in cls_obj._meta.local_fields]),
            "table_data": self.values(cls_obj, **self.kwargs),
        }
        data["top_header"]["spread"] = len(data['table_header'])
        
        return data
    
    def generate(self):
        for cls_obj in self.classes:
            yield self._get_data(cls_obj)
    
    @staticmethod
    def values(cls_obj, **kwargs):
        return cls_obj.objects.filter(**kwargs).values_list()


# class ProductGeneratorTemplate(object):
#     """Генератор отчётов по инстансам базовых классов с произвольным фильтром"""
#
#     def __init__(self, products, *args, **kwargs):
#         self.products = products
#         self.local_fields = None
#         self.kwargs = kwargs
#
#     def generate(self, cls_obj):
#         data = {
#             "top_header": {
#                 'spread': None,
#                 'row': [],
#                 'name': str(cls_obj._meta.verbose_name),
#             },
#             "table_header": OrderedDict([("", "")]),
#             "table_data": self.values(cls_obj, **self.kwargs),
#         }
#         data["top_header"]["spread"] = len(data['table_header'])
#
#         return data
#
#
#
#     @staticmethod
#     def values(cls_obj, **kwargs):
#         return cls_obj.objects.filter(**kwargs).values_list()