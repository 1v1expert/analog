import openpyxl
from collections import OrderedDict

from .choices import *
from .models import *
from django.db import models


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

        self.unique_manufacturer, self.unique_class, self.unique_subclass = set(), set(), set()
        self.unique_type_attributes, self.unique_value_attributes = set(), set()
        
        self.products = []
    
    def get_structured_data(self):
        self.to_separate()
        
        for opt in range(5, len(self.attributes) + 4):
            self.unique_type_attributes.add(self.attributes[opt])
            self.unique_value_attributes.add(self.options[opt])
        
        for product in self.body:
            structured_product, attributes = {}, []
            
            self.unique_class.add(product[1])
            self.unique_subclass.add(product[2])
            self.unique_manufacturer.add(product[4])
            
            for key in product.keys():
                if key < 5:
                    structured_product.update({
                            STRUCTURE_PRODUCT[key][1]: product[key]
                    })
                else:
                    attributes.append({
                        "type": TYPES_REV_DICT.get(self.attributes[key]),
                        "name": self.options[key],
                        "value": product[key]
                        })
            structured_product.update({
                STRUCTURE_PRODUCT[5][1]: attributes
            })
            
            self.products.append(structured_product)
            
        # TODO: make correctly check_exists
        #resp = self.check_exists_category()
        
        
    
    def to_separate(self):
        self.attributes = self.data[self.ATTRIBUTE_LINE]
        self.options = self.data[self.OPTION_LINE]
        self.body = self.data[self.OPTION_LINE+1:]
    
    def create_products(self, request):
        
        for product in self.products:
            created = False
            try:
                category = Category.objects.get(title__icontains=product['subclass'],
                                                parent__title__icontains=product['class'])
            except Category.DoesNotExist:
                print('Category does not exists ', product['class'], product['subclass'])
                continue
                
            try:
                manufacturer = Manufacturer.objects.get(title__icontains=product['manufacturer'])
            except Manufacturer.DoesNotExist:
                print('Manufacturer does not exists', product['manufacturer'])
                continue
            try:
                Product.objects.get(article=product['vendor_code'], manufacturer=manufacturer)
            except Product.DoesNotExist:
                created = True
                obj_product = Product(article=product['vendor_code'],
                                      manufacturer=manufacturer,
                                      title=product['name'],
                                      category=category,
                                      created_by=request.user)
            
            # obj_product, created = Product.objects.get_or_create(article=product['vendor_code'], manufacturer=manufacturer,
            #                                             defaults={
            #                                                 "title": product['name'],
            #                                                 "category": category,
            #                                                 "created_by": request.user
            #                                             })
            if created:
                for attr in product['attributes']:
                    try:
                        print(attr)
                        if attr.get('type'):
                            attribute = Attribute.objects.get(type=attr['type'],
                                                              category=category,
                                                              title__icontains=attr['name'])
                            attr_val = AttributeValue(title=attr['value'],
                                                      attribute=attribute,
                                                      created_by=request.user
                                                      )

                            obj_product.updated_by = request.user
                            obj_product.save()
                            
                            
                            
                            attr_val.updated_by = request.user
                            attr_val.save()
                            attr_val.products.add(obj_product)

                            obj_product.attrs_vals.add(attr_val)
                            obj_product.save()
                            #attr_val.save()
                            
                            
                            #obj_product.save()
                            
                        # else:
                        #     raise
                    except Exception as e:
                        print(e)
                        pass #raise
                    
            
            
        
    def check_exists_category(self):
        
        try:
            class_list = list(self.unique_class)
            subclass_list = list(self.unique_subclass)
            if (len(class_list) > 1) or (len(subclass_list) > 1):
                return "Too many class or subclass: {}, {}".format(class_list, subclass_list)
            else:
                category = Category.objects.get(title__icontains=class_list[0],
                                                parent__title__icontains=subclass_list[0])
        except:
            return "Not found class or subclass"
        
        print(self.unique_type_attributes, self.unique_value_attributes, self.unique_manufacturer, self.unique_class, self.unique_subclass)
    
    def get_attribute(self):
        pass
    