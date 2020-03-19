from django.db.models import Count
from django.core.management.base import BaseCommand
from django.contrib.auth import models as auth_md
from django.core.mail import EmailMessage

from datetime import datetime
import time

from catalog.reporters import generators, writers
from catalog.models import Manufacturer, Category, Attribute, FixedValue, Product
from catalog.internal.messages import _get_connection
from catalog.utils import SearchProducts

from app.models import MainLog


class SearchTable(object):
    """ Automatic search for analogues """
    def __init__(self, full=False):
        self.start_time = time.time()
        self.lead_time = 0
        self.user = auth_md.User.objects.get(is_staff=True, username='admin')
        
        self.manufacturers = Manufacturer.objects.all()
        if full:
            self.products = Product.objects.all()
        else:
            self.products = Product.objects.filter(is_updated=False)
    
    def build(self):
        print('{} products'.format(self.products.count()))
        for i, manufacturer in enumerate(self.manufacturers):
            print('{}/{} from {}'.format(i, self.manufacturers.count(), manufacturer.title))
            
            products = self.products.filter(manufacturer=manufacturer)
            print('{} products from {}'.format(products.count(), manufacturer.title))
            # need_manufactures = Manufacturer.objects.exclude(pk=manufacturer.pk)
        
            for product in products:
                raw = product.raw
                if raw is not None:
                    analogs = raw.get('analogs', None)
                else:
                    raw, analogs = {}, {}
            
                if not analogs:
                    raw.update(
                        {'analogs': {},
                         'errors': False,
                         'description': None
                         })
            
                for mm in self.manufacturers:
                    result = SearchProducts(product=product, manufacturer_to=mm)
                    try:
                        result.global_search()
                        if result.founded_products is None or not result.founded_products.exists():
                            analog = {mm.title: None}
                        else:
                            analog = {mm.title: result.founded_products.first().pk}
                    
                        raw['analogs'].update(analog)
                        # product.raw = {
                        #     'analogs': {}
                        # }
                    except Exception as e:
                        raw.update({
                            'errors_%s' % mm.title: True,
                            'description_%s' % mm.title: str(e),
                            'errors': True
                        })
                    finally:
                        del result
                
                product.is_enabled = True
                product.raw = raw
                product.is_updated = True
                product.save()
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lead_time = time.time() - self.start_time
        message = 'The database data processing was launched, completed in %s seconds' % str(self.lead_time)
        MainLog(user=self.user,
                message=message
                ).save()
        # return True


class Command(BaseCommand):
    help = 'Automatic search for analogues'

    def handle(self, *args, **options):
        with SearchTable() as st:
            st.build()
