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
        
        for manufacturer in Manufacturer.objects.all():
            
            products = Product.objects.filter(manufacturer=manufacturer)
            need_manufactures = Manufacturer.objects.exclude(pk=manufacturer.pk)
            
            for product in products[:10]:
                raw = product.raw
                for mm in need_manufactures:
                    result = SearchProducts(product=product, manufacturer_to=mm)
                    try:
                        result.global_search()
                        if not result.founded_products.exist():
                            continue
                        analog = {mm.title: result.founded_products.first().pk}
                        analogs = raw.get('analogs', default=None)
                        
                        if analogs is not None:
                            raw['analogs'].update(analog)
                        else:
                            raw.update(
                                {'analogs': analog,
                                'errors': False
                                 })
                        # product.raw = {
                        #     'analogs': {}
                        # }
                    except Exception as e:
                        product.raw = {
                            'errors': True,
                            'description': str(e)
                        }
                    finally:
                        del result
                        product.save(update_fields=raw)
