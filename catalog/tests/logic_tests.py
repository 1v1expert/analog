from catalog.models import Product, Category
import time


class LogicTest(object):
    """ Category checking """
    def __init__(self):
        self.categories = None
        self.start_time = time.time()
    
    def start(self):
        self.categories = self._get_categories()
    
    @staticmethod
    def _get_categories():
        return Category.objects.filter(parent=None)
