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
    
    def get_structured_data(self, request):
        self.to_separate()
        
        for opt in range(5, len(self.attributes) + 4):
            self.unique_type_attributes.add(self.attributes[opt])
            self.unique_value_attributes.add(self.options[opt])
        
        for product in self.body:
            if not product:
                continue
            structured_product, attributes = {}, []
            
            self.unique_class.add(product[1])
            self.unique_subclass.add(product[2])
            self.unique_manufacturer.add(product[4])
            #print(self.options)
            for key in product.keys():
                if key < 5:
                    structured_product.update({
                            STRUCTURE_PRODUCT[key][1]: product[key]
                    })
                else:
                    attributes.append({
                        "type": TYPES_REV_DICT.get(self.attributes[key].lower()),
                        "name": self.options[key],
                        "value": product[key]
                        })
            structured_product.update({
                STRUCTURE_PRODUCT[5][1]: attributes
            })
            
            is_valid_data = self.check_exists_types(structured_product)
            if isinstance(is_valid_data, str):
                return False, is_valid_data
            else:
                self.products.append(is_valid_data)
        self.create_products(request)
        return True, 'Success'
        
        # TODO: make correctly check_exists
        #resp = self.check_exists_category()
        
    def to_separate(self):
        self.attributes = self.data[self.ATTRIBUTE_LINE]
        self.options = self.data[self.OPTION_LINE]
        self.body = self.data[self.OPTION_LINE+1:]
    
    def create_products(self, request):
        
        for product in self.products:
            new_product = Product(article=product['vendor_code'],
                                  manufacturer=product['manufacturer_obj'],
                                  title=product['name'],
                                  category=product['category_obj'],
                                  created_by=request.user)

            for attr in product['attributes']:

                if attr.get('type'):
                    attr_val = AttributeValue(title=attr['value'],
                                              attribute=attr['attr_obj'],
                                              created_by=request.user
                                              )

                    new_product.updated_by = request.user
                    new_product.save()
                    
                    attr_val.updated_by = request.user
                    attr_val.save()
                    attr_val.products.add(new_product)

                    new_product.attrs_vals.add(attr_val)
                    #obj_product.save()
                    #attr_val.save()
                    
                    

                    
    def check_exists_types(self, product):
        # check manufacturer
        try:
            manufacturer = Manufacturer.objects.get(title__icontains=product.get('manufacturer'))
        except Manufacturer.DoesNotExist:
            return 'Ошибка! Не найден производитель товаров: {}'.format(product.get('manufacturer'))
        # check category
        try:
            category = Category.objects.get(title__iexact=product['subclass'],
                                            parent__title__iexact=product['class'])
        except Category.DoesNotExist:
            return 'Ошибка! Не найден класс {} с подклассом {}'.format(product['class'], product['subclass'])
        except Category.MultipleObjectsReturned:
            return 'Ошибка! Найдено более одного подкласса {} с классом {}'.format(product['subclass'], product['class'])
        # check product
        try:
            Product.objects.get(article=product['vendor_code'], manufacturer=manufacturer)
            return 'Ошибка! Наден продукт с наименованием - {} и производителем товара - {} в БД'.format(
                product['vendor_code'], manufacturer.title)
        except Product.DoesNotExist:
            pass
        except Product.MultipleObjectsReturned:
            return 'Ошибка! Найдено несколько продуктов с наименованием - {} и производителем товара - {} в БД'.format(
                product['vendor_code'], manufacturer.title)
        # check attributes
        for attr in product['attributes']:
            try:
                attribute = Attribute.objects.get(type=attr['type'], category=category, title__icontains=attr['name'])
                attr.update({"attr_obj": attribute})
            except Attribute.DoesNotExist:
                return 'Ошибка! Не найден атрибут с типом: {} - {} и наименованием {} в категории {}'.format(TYPES_DICT[attr['type']],
                                                                                                             category.pk, attr['name'], category)
            except Attribute.MultipleObjectsReturned:
                return 'Ошибка! Найдено несколько атрибутов с типом: {} и наименованием {}'.format(TYPES_DICT[attr['type']], attr['name'])
        
        product.update({
            "manufacturer_obj": manufacturer,
            "category_obj": category
        })
        
        return product
        
        
        # try:
        #     class_list = list(self.unique_class)
        #     subclass_list = list(self.unique_subclass)
        #     if (len(class_list) > 1) or (len(subclass_list) > 1):
        #         return "Too many class or subclass: {}, {}".format(class_list, subclass_list)
        #     else:
        #         category = Category.objects.get(title__icontains=class_list[0],
        #                                         parent__title__icontains=subclass_list[0])
        # except:
        #     return "Not found class or subclass"
        #
        # print(self.unique_type_attributes, self.unique_value_attributes, self.unique_manufacturer, self.unique_class, self.unique_subclass)
        #
    def get_attribute(self):
        pass
    