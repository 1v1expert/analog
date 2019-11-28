from django.db.models import Count
from django.core.management.base import BaseCommand
from django.contrib.auth import models
from django.core.mail import EmailMessage

from datetime import datetime


from catalog.reporters import generators, writers
from catalog.models import Manufacturer, Category, Attribute, FixedValue, Product
from catalog.internal.messages import _get_connection
from catalog.utils import SearchProducts

from app.models import MainLog


class Command(BaseCommand):
    help = 'Automatic search for analogues'

    def handle(self, *args, **options):
        manufacturers = Manufacturer.objects.all()
        for manufacturer in manufacturers:
            
            products = Product.objects.filter(manufacturer=manufacturer)
            # need_manufactures = Manufacturer.objects.exclude(pk=manufacturer.pk)
            
            for product in products[:10]:
                raw = product.raw
                analogs = raw.get('analogs', None)
                
                if analogs is not None:
                    raw['analogs'].update({})
                else:
                    raw.update(
                        {'analogs': {},
                         'errors': False,
                         'description': None
                         })
                
                for mm in manufacturers:
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
                            'description': str(e),
                            'errors': True
                        })
                    finally:
                        del result
                
                product.raw = raw
                product.save()
