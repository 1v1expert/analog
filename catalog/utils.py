import openpyxl
from collections import OrderedDict

class XLSDocumentReader(object):
    lines_header = 4
    
    def __init__(self, path=None, workbook=None):
        assert path or workbook, "You should provide either path to file or XLS-object"

        if workbook:
            self.workbook = workbook
        else:
            self.workbook = openpyxl.load_workbook(path,
                                                   read_only=True,
                                                   data_only=True)
        self.xlsx = path
        self.ws = self.workbook.active
        self.sheet = self.workbook.active
        # self.request = request
        # self.sender = sender
        # For errors
        # self.header_matrix_reversed_map = {(v[0] if isinstance(v, (list, tuple)) else v): k for k, v in self.header_matrix_map.items()}
        # self.table_row_reversed_map = {(v[0] if isinstance(v, (list, tuple)) else v): k for k, v in self.table_row_map.items()}
        self.errors = {}
        self.all_errors = {}
        self.document = {}
        self.attributes = {}
        self.options = {}
        self.values = []
        self.doc = []
        
    def get_full_data(self):
        line = {}
        rows = self.sheet.rows
        for cnt, row in enumerate(rows):
            for cnt_c, cell in enumerate(row):
                line.update({cnt_c: cell.value})
            self.doc.append(line)
            
    def parse_header(self, cnt, row):
        #values = []
        
        if cnt == 1:
            for cnt_c, cell in enumerate(row):
                if cell.value and cnt_c > 4:
                    self.attributes.update({cnt_c: cell.value})
        elif cnt == 3:
            for cnt_c, cell in enumerate(row):
                self.options.update({cnt_c: cell.value})

    def parse_body(self, cnt, row):
        #values = []
        data = {}
        for cnt_c, cell in enumerate(row):
            if cell.value:
                data[cnt_c] = cell.value
        return data
        #self.values
        
    def get_data(self):
        rows = self.sheet.rows
        for cnt, row in enumerate(rows):
            if cnt < 4:
                self.parse_header(cnt, row)
            else:
                self.values.append(self.parse_body(cnt, row))
        return {
            'values': self.values,
            'options': self.options,
            'attributes': self.attributes
        }


class FillingDB(object):
    
    def __init__(self, data):
        self.data = data
    
    def main_cycle(self):
        for line in self.data.get('values', None):
            pass
    
    def check_exists(self):
        pass
    
    def get_attribute(self):
        pass