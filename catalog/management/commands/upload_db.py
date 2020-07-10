from django.core.management.base import BaseCommand

from catalog.file_utils import NorthAurora

import logging

from time import time, strftime, gmtime

# Get an instance of a logger
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

        document = NorthAurora(path=filename, only_parse=False, loadnetworkmodel=False).parse_file(sheet_name='НЛЗС')
        logger.debug('Файл {} загружен, {} позиций, дублей - {}'.format(
            filename, document.c_lines, len(document.doubles_article)
        ))

        logger.debug('Время потраченное на загрузку: {}'.format(
            strftime("%H:%M:%S", gmtime(time() - document.start_time))))



