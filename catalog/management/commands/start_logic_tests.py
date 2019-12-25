from django.core.management.base import BaseCommand
from catalog.tests import logic_tests


class Command(BaseCommand):
    help = 'Automatic category checking'

    def handle(self, *args, **options):
        tests = logic_tests.LogicTest(enable_msg=True)
        tests.generate_doc()
