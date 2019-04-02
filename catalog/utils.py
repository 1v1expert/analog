import openpyxl
from collections import OrderedDict

from .choices import *


class XLSDocumentReader(object):
    
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
        
    def parse_file(self):
        rows = self.sheet.rows
        for cnt, row in enumerate(rows):
            line = {}
            for cnt_c, cell in enumerate(row):
                if cell.value:
                    line.update({cnt_c: cell.value})
            self.doc.append(line)
        return self.doc
    

class ProcessingUploadData(object):
    """Класс преобразования считанных данных из загружаемого файла
    products = [product1, product2, ...]
    product = {
        name: name,
        class: class,
        subclass: subclass,
        vendor_code: vendor_code,
        manufacturer: manufacturer,
        attributes: [attr1, attr2, ...]
    }
    attribute = {
        type: type.
        value: value,
        name: name
    }
    """
    def __init__(self, data):
        self.ATTRIBUTE_LINE = 1
        self.OPTION_LINE = 3
        
        self.data = data
        self.attributes = []
        self.options = []
        self.body = []
        
        self.products = []
    
    def get_structured_data(self):
        self.to_separate()
        
        for product in self.body:
            structured_product, attributes = {}, []
            for key in product.keys():
                if key < 5:
                    structured_product.update({
                            STRUCTURE_PRODUCT[key][1]: product[key]
                    })
                else:
                    attributes.append({
                        "type": self.attributes[key],
                        "name": self.options[key],
                        "value": product[key]
                        })
            structured_product.update({
                STRUCTURE_PRODUCT[5][1]: attributes
            })
            
            self.products.append(structured_product)
        
        return self.products
    
    def to_separate(self):
        self.attributes = self.data[self.ATTRIBUTE_LINE]
        self.options = self.data[self.OPTION_LINE]
        self.body = self.data[self.OPTION_LINE+1:]
    
    def check_exists_category(self):
    
    
    def get_attribute(self):
        pass
    