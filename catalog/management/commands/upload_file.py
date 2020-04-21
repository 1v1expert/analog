from django.core.management.base import BaseCommand

from catalog.file_utils import NorthAurora

import logging

import time

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

        document = NorthAurora(path=filename, only_parse=False, loadnetworkmodel=False).parse_file(sheet_name='НПЛ6')
        logger.debug('Файл {} загружен, {} позиций, дублей - {}'.format(
            filename, document.c_lines, len(document.doubles_article)
        ))
        all_time = time.time() - document.start_time
        h = all_time // 3600
        m = (all_time // 60) % 60
        s = all_time % 60
        logger.debug('Время потраченное на загрузку: {}h {}m {}s'.format(
            h, m, s ))




