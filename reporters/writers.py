import xlsxwriter
import csv
from django.conf import settings


class BookkeepingWriter(object):
    def __init__(self, name):
        self.filename = name
        
    def dump(self, data):
        # self.write_top_header(**data['top_header'])
        self.write_table_header(data['table_header'].values())
        # FIXME: make use of `for k in data['table_header']`
        for row in data['table_data']:
            self.write_table_row(row.values())
    
    def write_top_header(self):
        pass
    
    def write_table_header(self, row):
        base_opts = {'text_wrap': 1, 'align': 'left', 'valign': 'vcenter', 'left': 1, 'right': 1, 'top': 2,
            'bottom': 2, }
        default_format = self._wb.add_format(base_opts)
    
        for col, cell in enumerate(row):
            new_format = None
            if col == 0:
                new_format = self._wb.add_format(base_opts)
                new_format.set_left(2)
            elif col == len(row) - 1:
                new_format = self._wb.add_format(base_opts)
                new_format.set_right(2)
        
            self._default_ws.set_column(col, col, min(15, len(str(cell))))
            self._default_ws.write(self._row, col, cell, new_format or default_format)
    
        max_len = max(sorted([len(str(x)) for x in row]))
        self._default_ws.set_row(self._row, (15 * max_len // 15) + 1)
        self._row += 1
    
    def write_table_row(self, row):
        self.writerow(row, self.formats['table_row'])
    
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
