from django.db.models import Count
from django.core.management.base import BaseCommand
from django.contrib.auth import models
from django.core.mail import EmailMessage

from datetime import datetime


from catalog.reporters import generators, writers
from catalog.models import Manufacturer, Category, Attribute, FixedValue
from catalog.internal.messages import _get_connection

from app.models import MainLog


class Command(BaseCommand):
    help = 'Generate a monthly base dump file'

    def handle(self, *args, **options):
        manufactures = Manufacturer.objects.all()
        user = models.User.objects.get(is_staff=True, username='tech')
        
        meta_data = generators.AdditionalGeneratorTemplate((models.User, Manufacturer, Category, Attribute, FixedValue))
        data = generators.DefaultGeneratorTemplate(manufactures)
        
        filename = None
        name = 'Monthly base dump - {}'.format(datetime.now().date())
        
        try:
            with writers.BookkeepingWriter(name, user) as writer:
                writer.dump(meta_data.generate())
                writer.dump(data.generate())
                filename = writer.filename
        except Exception as e:
            MainLog.objects.create(user=user, raw={'error': e}, has_errors=True, message=name)

        msg = EmailMessage(
            subject='Subject of the Email',
            body='Body of the email',
            from_email='info@analogpro.ru',
            to=['1v1expert@gmail.com'],
            connection=_get_connection())
        if filename:
            msg.attach_file(filename, 'application/xls')
        response = msg.send()
        MainLog.objects.create(user=user, raw={'response': response}, message=name)
