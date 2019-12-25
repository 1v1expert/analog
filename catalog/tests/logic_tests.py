from catalog.models import Product, Category, Attribute
from catalog.reporters import generators
import time
from pprint import pprint
from collections import OrderedDict
from django.contrib.auth import models
from catalog.reporters import writers
from datetime import datetime


class LogicTest(object):
    """ Category checking """
    def __init__(self, enable_msg=False):
        self.categories = None
        self.start_time = time.time()
        self.enable_msg = enable_msg
        self.failed_attributes = []
    
    def start(self) -> list():
        result = []
        
        for category in self._get_categories():
            result.append(self._get_category_statistic(category))
        
        if self.enable_msg:
            end_time = time.time() - self.start_time
            pprint(result)
            print("Time left %s" % str(end_time))
        
        return result
    
    @staticmethod
    def _get_categories() -> Category.objects:
        return Category.objects.exclude(parent=None)[:10]
    
    def _get_category_statistic(self, category: Category) -> dict:
        """ {"category": title,
             "count": count,
             "attributes": [
                "attribute": title,
                "count": count,
                "per_count": per_count,
                "type": attribute_type
                ]
             } """
        # products = Product.objects.filter(category=category)
        attributes = category.attributes.filter(type='hrd')
        products = Product.objects.filter(category=category)
        products_count = products.count()
        
        if not products_count:
            return {
                "category": category.title,
                "count": products_count,
                "attributes": []
            }
        
        result = {
            "category": category.title,
            "count": products_count,
            "attributes": []
        }

        for attribute in attributes:
            fixed = True
            if attribute.title in ('вид', 'покрытие', 'ед.изм', 'форма', 'удвоение'):
                count = products.filter(fixed_attrs_vals__attribute=attribute).count()
            else: # 'длина', 'толщина', 'высота борта', 'ширина доп.', 'ширина', 'высота борта доп.', 'цена', 'длина', 'основание', 'ширина', 'диаметр', 'резьба'
                # todo: should check on not null
                count = products.filter(unfixed_attrs_vals__attribute=attribute).count()
                fixed = False
                
            result['attributes'].append({"name": attribute.title,
                                         "type": attribute.get_type_display(),
                                         "count": count,
                                         "pk": attribute.pk,
                                         "per_count": round(count * 100 / products_count)})
            
            if count < 100:
                self.failed_attributes.append({
                    "category_pk": category.pk,
                    "attribute_pk": attribute.pk,
                    "fixed": fixed
                })
                
        return result
    
    @staticmethod
    def to_xls(raw_data) -> list():
        attributes = list(Attribute.objects.filter(type='hrd').values_list('id', 'title'))
        
        def kakayato_func(raw_data):
            
            for i, category in enumerate(raw_data):
                line = [('seq', i),
                        ('title', category['category']),
                        ('count', category['count']),
                        ]
                
                for attribute in attributes:
                    
                    count = '----'
                    for attr in category['attributes']:
                        if attr['pk'] == attribute[0]:
                            count = attr['count']
                
                    line.append((attribute[0], count))
                
                yield OrderedDict(line)
                # resp.append(OrderedDict(line))

        list1 = {
            "top_header": {
                'spread': None,
                'row': [],
                'name': "Статистика по жестким атр-ам",
            },
            "table_header": OrderedDict([
                                            ('seq', '№ п/п'),
                                            ('title', 'Наименование подкласса'),
                                            ('count', 'Всего позиций в подклассе'),
                                        ] + attributes
                                        ),
            
            "table_data": kakayato_func(raw_data)
        }
        list1["top_header"]["spread"] = len(list1['table_header'])
        
        return [list1, ]
    
    def generate_fail_products(self):
        result = []
        for fail in self.failed_attributes:
            products = Product.objects.filter(category__pk=fail['category_pk'],
                                              unfixed_attrs_vals__attribute__pk=fail['attribute_pk'])
            if fail['fixed']:
                products = Product.objects.filter(category__pk=fail['category_pk'],
                                                  fixed_attrs_vals__attribute__pk=fail['attribute_pk'])
                
            result.append(generators.DefaultGeneratorTemplate()._get_data(name_sheet='ss', products=products))
            
        return result
        
    def generate_doc(self):
        user = models.User.objects.get(username='tech')
        
        with writers.BookkeepingWriter('Статистика по подклассам {}'.format(datetime.now().date()), user) as writer:
            to_dump = self.to_xls(self.start()) + self.generate_fail_products()
            writer.dump(to_dump)
