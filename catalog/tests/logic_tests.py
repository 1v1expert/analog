from catalog.models import Product, Category, Attribute
from catalog.reporters import generators
import time
from pprint import pprint
from collections import OrderedDict
from django.contrib.auth import models
from catalog.reporters import writers
from datetime import datetime


class AttributeReport(object):
    """ Category checking """
    def __init__(self, enable_msg=False):
        self.categories = None
        self.start_time = time.time()
        self.enable_msg = enable_msg
        self.failed_attributes = []
        self.report = []
    
    def start(self) -> list():

        for category in self._get_categories():
            self.report.append(self._get_category_statistic(category))
        
        if self.enable_msg:
            end_time = time.time() - self.start_time
            pprint(self.report)
            print("Time left %s" % str(end_time))
        
        return self.report
    
    @staticmethod
    def _get_categories() -> Category.objects:
        return Category.objects.exclude(parent=None)

    def _get_category_statistic(self, category: Category) -> dict:
        """ проверка сколько позиций содержат в себе жесткие атрибуты
        {"category": title,
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
        
        if not products_count:  # if not have products in category
            return {
                "category": category.title,
                "count": products_count,
                "attributes": []
            }
        
        report = {
            "category": category.title,
            "count": products_count,
            "attributes": []
        }

        for attribute in attributes:
            if attribute.title in ('вид', 'покрытие', 'ед.изм', 'форма', 'удвоение'):
                count = products.filter(fixed_attrs_vals__attribute=attribute).count()
                query = products.exclude(fixed_attrs_vals__attribute=attribute)
            else:  # 'длина', 'толщина', 'высота борта', 'ширина доп.', 'ширина', 'высота борта доп.', 'цена', 'длина', 'основание', 'ширина', 'диаметр', 'резьба'
                # todo: should check on not null
                count = products.filter(unfixed_attrs_vals__attribute=attribute).count()
                query = products.exclude(unfixed_attrs_vals__attribute=attribute)

            per_count = round(count * 100 / products_count)
            report['attributes'].append({"name": attribute.title,
                                         "type": attribute.get_type_display(),
                                         "count": count,
                                         "pk": attribute.pk,
                                         "per_count": per_count})
            
            if per_count < 100:
                self.failed_attributes.append({
                    # "category_pk": category.pk,
                    # "attribute_pk": attribute.pk,
                    # "fixed": fixed,
                    "query": query,
                    "category_name": category.title,
                    "attribute_name": attribute.title
                })
                
        return report
    
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
                    
                    count, per_count = '----', '-'
                    for attr in category['attributes']:
                        if attr['pk'] == attribute[0]:
                            count = attr['count']
                            per_count = attr['per_count']
                    line.append((attribute[0], '{}/{}%'.format(count, per_count)))
                
                yield OrderedDict(line)

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
            result.append(generators.DefaultGeneratorTemplate()._get_data(
                name_sheet='{}({})'.format(fail['category_name'][:15], fail['attribute_name'][:15]),
                products=fail['query'])
            )
            # products = Product.objects.filter(category__pk=fail['category_pk'],
            #                                   unfixed_attrs_vals__attribute__pk=fail['attribute_pk'])
            # if fail['fixed']:
            #     products = Product.objects.filter(category__pk=fail['category_pk'],
            #                                       fixed_attrs_vals__attribute__pk=fail['attribute_pk'])
            
            # result.append(generators.DefaultGeneratorTemplate()._get_data(
            #     name_sheet='{}({})'.format(fail['category_name'][:15], fail['attribute_name'][:15]), products=products))
        #
        return result
        
    def generate_doc(self):
        user = models.User.objects.get(username='tech')
        
        if self.report:
            with writers.BookkeepingWriter(
                    'Статистика по подклассам {}'.format(datetime.now().date()), user
            ) as writer:
                to_dump = self.to_xls(self.report) + self.generate_fail_products()
                writer.dump(to_dump)
