from django.core.management.base import BaseCommand
from catalog.tests import logic_tests


class Command(BaseCommand):
    help = 'Automatic category checking'

    def handle(self, *args, **options):
        tests = logic_tests.AttributeReport(enable_msg=True)
        tests.start()
        tests.generate_doc()

