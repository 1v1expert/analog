from django.utils.timezone import datetime

from django.core.management.base import BaseCommand


import time

from catalog.file_utils import ProcessingUploadData, PKT, NorthAurora

import logging

# Get an instance of a logger
logger = logging.getLogger('analog')


class Command(BaseCommand):
    """ Update DataBase"""
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--filename", action="store_true",
        )
    
    def handle(self, *args, **options):
        filename = options["filename"]
        if not filename:
            filename = 'files/north_aurora.xlsx'

        document = NorthAurora(path=filename,
                                                         only_parse=False,
                                                         loadnetworkmodel=False).parse_file()
        logger.debug('Файл {} загружен, {} позиций, дублей - {}'.format(
            filename, document.c_lines, len(document.doubles_article)
        ))
        # reader = NorthAurora(path=filename, sheet_name='Companys')
        # data = reader.parse_file()
        # self.companys_update(data)

        # created, error = ProcessingUploadData(
            # XLSDocumentReader(path=filename).parse_file(), start_time=time.time()
        # ).get_structured_data(request)
        
        # PKT(path=filename, only_parse=False).parse_file()




