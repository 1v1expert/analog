from catalog.models import Product, Category
import time
from pprint import pprint


class LogicTest(object):
    """ Category checking """
    def __init__(self, enable_msg=False):
        self.categories = None
        self.start_time = time.time()
        self.enable_msg = enable_msg
    
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
    
    @staticmethod
    def _get_category_statistic(category: Category) -> dict:
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
                "count": products_count
            }
        
        result = {
            "category": category.title,
            "count": products_count,
            "attributes": []
        }
        
        for attribute in attributes:
            if attribute.title in ('вид', 'покрытие', 'ед.изм', 'форма', 'удвоение'):
                count = products.filter(fixed_attrs_vals__attribute=attribute).count()
            else: # 'длина', 'толщина', 'высота борта', 'ширина доп.', 'ширина', 'высота борта доп.', 'цена', 'длина', 'основание', 'ширина', 'диаметр', 'резьба'
                # todo: should check on not null
                count = products.filter(unfixed_attrs_vals__attribute=attribute).count()
                
            result['attributes'].append({"name": attribute.title,
                                         "type": attribute.get_type_display(),
                                         "count": count,
                                         "per_count": round(count * 100 / products_count)})
        return result
    
    def export_data(self, data):
        pass
