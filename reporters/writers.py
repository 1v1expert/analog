import xlsxwriter
import csv
from django.conf import settings


class BookkeepingWriter(object):
    def __init__(self, name):
        self.filename = name
        
    def dump(self, data):
        pass
    
    def writerow(self, row, fmt):
        # TODO: this is way too ugly and must be rewritten.
        for col, item in enumerate(row):
            c_fmt = fmt
            self._default_ws.write(self._row, col, item, c_fmt)
        self._row += 1
    
    def __enter__(self):
        self._wb = xlsxwriter.Workbook(self.filename,
                                       {'default_date_format': 'dd.mm.yyyy'}
        )
        self._default_ws = self._wb.add_worksheet()
        self._row = 0
        self._col = 0
        self.formats = {
            'top_header': self._wb.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'bold': 1}),
            'formula': self._wb.add_format({
                'align': 'left',
                'valign': 'vcenter'}),
            'table_row': self._wb.add_format({
                'align': 'left',
                'valign': 'vcenter',
                'border': 1})
        }
        return self

    def __exit__(self, _type, value, tb):
        self._wb.close()


def dump_csv(name, data):
    with open('{}/{}'.format(settings.FILES_ROOT, name), 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, dialect='excel')
        for row in data:
            writer.writerow(row)
