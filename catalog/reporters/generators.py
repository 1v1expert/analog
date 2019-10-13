from collections import OrderedDict, defaultdict
import datetime

from catalog.models import Product, Attribute


class DefaultGeneratorTemplate(object):
    def __init__(self, manufactures):
        self.manufactures = manufactures
        self.date = datetime.datetime.now()
        self.attributes = Attribute.objects.values_list('title', flat=True)
    
    def _get_data(self, manufacturer) -> dict:
        data = {
            "top_header": {
                'spread': None,
                'row': [],
                'name': str(manufacturer)
            },
            "table_header": OrderedDict([
                                            ('seq', '№ п/п'),
                                            ('title', 'Наименование'),
                                            # ('manufacturer', 'Производитель'),
                                            ('article', 'Артикул'),
                                            ('additional_article', 'Доп. артикул'),
                                            ('series', 'Серия'),
                                            ('category', 'Категория'),
                                            # ('category_from_categories', 'Категория(перебор по словарю из классов)'),
                                            # ('category_from_product', 'Категория(смарт метод)'),
                                            # ('category_from_neural_network', 'категория(нейро-сеть)'),
                                        ] + list(Attribute.objects.values_list('id', 'title'))
                                        ),
            "table_data": self.do_products(manufacturer)
        }
        data["top_header"]["spread"] = len(data['table_header'])
    
        return data
    
    def generate(self) -> dict:
        for manufacturer in self.manufactures:
            yield self._get_data(manufacturer)
        
    def do_products(self, manufacturer) -> OrderedDict:
        for seq, product in enumerate(
                Product.objects.filter(manufacturer=manufacturer).prefetch_related('fixed_attrs_vals',
                                                                                        'fixed_attrs_vals__value',
                                                                                        'fixed_attrs_vals__attribute',
                                                                                        'unfixed_attrs_vals',
                                                                                        'unfixed_attrs_vals__attribute')
        ):
            yield OrderedDict([
                                  ('seq', seq),
                                  ('title', product.title),
                                  # ('manufacturer', product.manufacturer.title),
                                  ('article', product.article),
                                  ('additional_article', product.additional_article),
                                  ('series', product.series),
                                  ('category', product.category.title),
                                  # ('category_from_categories', product.raw['category_from_categories']),
                                  # ('category_from_product', product.raw['category_from_product']),
                                  # ('category_from_neural_network', product.raw['category_from_neural_network']),
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
    def __init__(self, cls):
        self.cls = cls
        self.local_fields = OrderedDict([(field['name'], field['verbose_name']) for field in cls._meta.local_fields])
    
    def generate(self):
        data = {
            "top_header": {
                'spread': None,
                'row': [],
                'name': self.cls._meta.verbose_name
            },
            "table_header": self.local_fields,
            "table_data": self.do_positions()
        }
        data["top_header"]["spread"] = len(data['table_header'])
    
        return data
    
    def do_positions(self):
        return self.cls.objects