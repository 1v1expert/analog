from django.core.management.base import BaseCommand

from catalog.file_utils import SubclassesReader, ProcessingUploadData, XLSDocumentReader
from django.contrib.auth import models as auth_md
import logging
from catalog.models import Category

# from time import time, strftime, gmtime
import time
# Get an instance of a logger
import traceback
logger = logging.getLogger('analog')


class Command(BaseCommand):
    """ Upload DataBase"""
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--filename", action="store_true",
        )
    
    def handle(self, *args, **options):
        filename = options["filename"]
        if not filename:
            filename = 'files/Subclasses.xlsx'
        #
        # Category.objects.exclude(parent=None).delete()
        # Category.objects.all().delete()
        # Category.objects.create(title='КНС',
        #                         created_by=auth_md.User.objects.get(is_staff=True, username='admin'),
        #                         updated_by=auth_md.User.objects.get(is_staff=True, username='admin')
        #                         )
        # try:
        #     document = SubclassesReader(path=filename, only_parse=False, loadnetworkmodel=False)
        #     print(document.parse_file()["body"])
        #     document.process()
        # except Exception as e:
        #     self.stdout.write(f'Wrong error>> {e}, {traceback.format_exc()}')
        # else:
        #     self.stdout.write(f'{document}')



        filename = 'files/Betterman_test.xlsx'
        created, error = ProcessingUploadData(
            XLSDocumentReader(path=filename).parse_file(), start_time=time.time()
        ).get_structured_data()

        if not created:
            self.stdout.write(f'{error}')
        
        
        
        # logger.debug('Файл {} загружен, {} позиций, дублей - {}'.format(
        #     filename, document.c_lines, len(document.doubles_article)
        # ))

        # logger.debug('Время потраченное на загрузку: {}'.format(
        #     strftime("%H:%M:%S", gmtime(time() - document.start_time))))



