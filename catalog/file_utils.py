import openpyxl
from openpyxl.utils.exceptions import InvalidFileException
from collections import OrderedDict

from catalog.choices import *
from catalog.models import *

from django.contrib import messages
from django.contrib.auth import models as auth_md
from django.db import models
from django.db.models.functions import Lower

import re
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger('analog')


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
                    line.update({cnt_c: str(cell.value)})
            self.doc.append(line)
            
        self.workbook._archive.close()
        return self.doc
        

class ProcessingUploadData(object):
    """Класс преобразования считанных данных из загружаемого файла
    products = [product1, product2, ...]
    product = {
        name: name,
        class: class,
        subclass: subclass,
        series: series,
        article: article,
        additional_article: additional_article,
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
    
    @staticmethod
    def is_digit(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
    def get_structured_data(self, request):
        self.to_separate()
        
        for opt in range(7, len(self.attributes) + 4):
            self.unique_type_attributes.add(self.attributes[opt])
            self.unique_value_attributes.add(self.options[opt])
        
        for count, line in enumerate(self.body):
            if count % 100 == 0:
                print('Line #{}'.format(count))
                messages.add_message(request, messages.INFO, 'Success processed {} lines'.format(count))
            if not line:
                continue
            structured_product, attributes = {}, []
            try:
                self.unique_class.add(line[1])
                self.unique_subclass.add(line[2])
                self.unique_manufacturer.add(line[4])
            except KeyError:
                return False, 'Error in line: {}'.format(line)
            #print(self.options)
            for key in line.keys():
                # print('Product: ', product[key])
                if key < 7:
                    structured_product.update({
                            STRUCTURE_PRODUCT[key][1]: line[key].lstrip().rstrip()
                    })
                else:
                    attributes.append({
                        "type": TYPES_REV_DICT.get(self.attributes[key].lower()),
                        "name": self.options[key].lstrip().rstrip(),
                        "value": float(line[key].replace(',', '.')) if self.is_digit(line[key].replace(',', '.')) else line[key].lstrip().rstrip(),
                        "is_digit": self.is_digit(line[key].replace(',', '.'))
                        })
            structured_product.update({
                STRUCTURE_PRODUCT[7][1]: attributes
            })
        
            is_valid_data = self.check_exists_types(structured_product)
            if isinstance(is_valid_data, str):
                print(structured_product, 'reason: {}'.format(is_valid_data))
                return False, is_valid_data
            else:
                self.products.append(is_valid_data)
        print('Check correct and finish, start create products')
        messages.add_message(request, messages.SUCCESS, 'Check correct and finish, start create products')
        self.create_products(request)
        return True, 'Success'
        
        # TODO: make correctly check_exists
        #resp = self.check_exists_category()
        
    def to_separate(self):
        self.attributes = self.data[self.ATTRIBUTE_LINE]
        self.options = self.data[self.OPTION_LINE]
        self.body = self.data[self.OPTION_LINE+1:]
    
    def create_products(self, request):
        
        def create_attr():
            # if attr.get('type'):
            if attr.get('is_digit'):
                attr_val = UnFixedAttributeValue(value=attr['value'], attribute=attr['attr_obj'],
                                                 created_by=request.user, updated_by=request.user)
            else:
                attr_val = FixedAttributeValue(value=attr['value'], attribute=attr['attr_obj'],
                                               created_by=request.user, updated_by=request.user)
                
            attr_val.save()
            attr_val.products.add(new_product)
            attr_val.save()
            if attr.get('is_digit'):
                new_product.unfixed_attrs_vals.add(attr_val)
            else:
                new_product.fixed_attrs_vals.add(attr_val)
                
        for count, product in enumerate(self.products):
            if count % 100 == 0:
                print('Line #{}'.format(count))
                messages.add_message(request, messages.INFO,
                                     'Success added {} products'.format(count))
            
            new_product = Product(article=product['article'],
                                  series=product.get('series', ""),
                                  additional_article=product.get('additional_article', ""),
                                  manufacturer=product['manufacturer_obj'],
                                  title=product['name'],
                                  category=product['category_obj'],
                                  created_by=request.user,
                                  updated_by=request.user)
            new_product.save()
            for attr in product['attributes']:
                create_attr()
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
            Product.objects.get(article=product['article'], manufacturer=manufacturer)
            return 'Ошибка! Наден продукт с наименованием - {} и производителем товара - {} в БД'.format(
                product['article'], manufacturer.title)
        except Product.DoesNotExist:
            pass
        except Product.MultipleObjectsReturned:
            return 'Ошибка! Найдено несколько продуктов с наименованием - {} и производителем товара - {} в БД'.format(
                product['article'], manufacturer.title)
        # check attributes
        for attr in product['attributes']:
            # find instance attribute
            try:
                attribute = Attribute.objects.get(type=attr['type'], category=category, title=attr['name'])
                attr.update({"attr_obj": attribute})
                # find fixed attribute
                if not attr['is_digit']:
                    fix_value = FixedValue.objects.get(title=attr['value'], attribute=attribute)
                    attr['value'] = fix_value
            except Attribute.DoesNotExist:
                return 'Ошибка! Не найден атрибут с типом: {} и наименованием {} в категории {}'.format(TYPES_DICT[attr['type']], attr['name'], category)
            except Attribute.MultipleObjectsReturned:
                return 'Ошибка! Найдено несколько атрибутов с типом: {} и наименованием {}'.format(TYPES_DICT[attr['type']], attr['name'])
            except FixedValue.DoesNotExist:
                return 'Ошибка! Не найден фикс. атрибут {} со значением {}'.format(attr['value'], attribute)
            #  todo: useful insert check FixedValue.DoesNotExist
        
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


class KOKSDocumentReader(object):
    """
    /code/article/title/price
    name sheet -> type
    """
    def __init__(self, path=None, workbook=None, only_parse=True, user=None):
        assert path or workbook, "You should provide either path to file or XLS-object"
        
        if workbook:
            self.workbook = workbook
        else:
            try:
                self.workbook = openpyxl.load_workbook(path,
                                                       read_only=True,
                                                       data_only=True)
            except InvalidFileException:
                # make read file another reader
                raise Exception('Invalid file')
        self.xlsx = path
        # self.ws = self.workbook.active
        self.sheet = self.workbook.active
        self.sheets = self.workbook.get_sheet_names()
        self.only_parse = False
        self.c_lines = 0
        
        self.user = user if user is not None else auth_md.User.objects.get(is_staff=True, username='admin')
        
        self.manufacturer = Manufacturer.objects.get(title='КОКС')
        self.hrd_attributes = FixedValue.objects.filter(attribute__type='hrd').annotate(title_lower=Lower('title'))\
            .only('title').values_list('title_lower', flat=True).distinct()
        
        self.products = []
        self.articles = set()
        self.doubles_article = []
        # self.fix_attr_vals = {}
        # self.unfix_attr_vals = {}
        self.attr_vals = {}
        
    # @staticmethod
    # def _get_data_from_line(row):
    #     for cell in row:
    #         yield str(cell.value)
    #
    def create_products(self, article, title, category, additional_article=""):
        product = Product(article=article,
                          additional_article=additional_article,
                          manufacturer=self.manufacturer,
                          title=title,
                          category=category,
                          created_by=self.user,
                          updated_by=self.user)
        logger.debug(product)
        self.products.append(product)
        self.attr_vals[article] = {
            'fix': [],
            'unfix': []
        }
        # self.fix_attr_vals[article] = []
        # self.unfix_attr_vals[article] = []
        
        # return product
    
    @staticmethod
    def _get_category(title):
        result = re.findall(r'\w+\d+', title)  # choose sizes
        result2 = re.findall(r'\w+', title)  # splite the line
        required_samples = set()
        for word in result2:
            if len(word) <= 4:
                continue
            coincided = False
            for size in result:
                if size in word:
                    coincided = True
                    break
            if not coincided:
                required_samples.add(word)
                
        copy_required_sample = required_samples.copy()
        # word_sample = required_samples.pop()
        # print(word_sample)
        for word_sample in list(copy_required_sample):
            selection = Product.objects.filter(title__icontains=word_sample)
            if selection.count():
                break
        product = selection.first()
        if product:
            return product.category
        else: return product
        # selection_c = selection.count()
        # if selection_c == 1:
        #     return selection.get().category
        # elif selection_c == 0:
        #     return None
        # else:  # narrowing the sample
        #     for sample in copy_required_sample:
        #         word_sample = required_samples.pop()
        #         n_selection = selection.filter(title__icontains=word_sample)
        #         if n_selection.count() == 0: return selection.first().category
        #         else:
        #             selection = n_selection
        # return selection.first().category

    def _finding_an_fix_attribute(self, title, article):
        value, attribute = None, None
        for attr in self.hrd_attributes:
            if attr in title:  # entry check is not the right decision
                value = attr
                break
        if value is not None:
            fixed_value = FixedValue.objects.get(title__iexact=value)
            self._create_attribute(article, fixed_value, fixed_value.attribute, fixed=True)
        pass
    
    def _create_attribute(self, article, value, attribute, fixed=False):
        if fixed:
            attr_val = FixedAttributeValue(value=value, attribute=attribute, created_by=self.user, updated_by=self.user)
            # self.fix_attr_vals[article].append(attr_val)
            self.attr_vals[article]['fix'].append(attr_val)
            
        else:
            attr_val = UnFixedAttributeValue(value=value, attribute=attribute, created_by=self.user, updated_by=self.user)
            # self.unfix_attr_vals[article].append(attr_val)
            self.attr_vals[article]['unfix'].append(attr_val)
        
        logger.debug(attr_val)
        attr_val.created_at = self.user
        attr_val.updated_by = self.user
        # attr_val.save()
    
    def line_processing(self, line, name_sheet=None):
        if not name_sheet:
            name_sheet = self.sheets[0]
        additional_article = line[0]
        article = line[1]
        title = line[2].lower()
        price = line[3].replace(',', '.')
        
        if not article.strip() or article == 'None':
            return
        
        self.c_lines += 1  # counter lines
        
        # check_doubles
        if article in self.articles:
            self.doubles_article.append(article)
            return
        self.articles.add(article)
        
        category = self._get_category(title)
        if category:
            self.create_products(article, title, category, additional_article=additional_article)
            self._finding_an_fix_attribute(title, article)  # finding fixed attributes in the product name
            if is_digit(price):  # create price attr
                attribute = Attribute.objects.get(title='цена')
                self._create_attribute(article, float(price), attribute, fixed=False)
            
            value = FixedValue.objects.get(title__icontains=sheet_names[name_sheet])
            attribute = Attribute.objects.get(title='покрытие')
            self._create_attribute(article, value, attribute, fixed=True)

        logger.debug('line {}, - {} - {}, category: {}'.format(self.c_lines, article, title, category))
        pass
    
    def read_sheet(self):
        rows = self.sheet.rows
        for cnt, row in enumerate(rows):
            if cnt in range(3):
                continue
            yield [str(cell.value) for cell in row]

    def parse_file(self):
        for name_list in self.sheets:
            logger.debug('Sheet {}'.format(name_list))
            self.sheet = self.workbook.get_sheet_by_name(name_list)
            for line in self.read_sheet():
                self.line_processing(line, name_list)
                
        self._create_attributes_and_products()
    
    def _create_attributes_and_products(self):
        if not self.only_parse:
            logger.debug('Start creating process: {}, {} products'.format(not self.only_parse, len(self.products)))
            Product.objects.bulk_create(self.products)
            
            for key in self.attr_vals.keys():
                product = Product.objects.get(article=key, manufacturer=self.manufacturer)
                for fix in self.attr_vals[key]['fix']:
                    fix.save()
                    fix.products.add(product)
                    fix.save()
                for unfix in self.attr_vals[key]['unfix']:
                    unfix.save()
                    unfix.products.add(product)
                    unfix.save()
                product.fixed_attrs_vals.set(self.attr_vals[key]['fix'])
                product.unfixed_attrs_vals.set(self.attr_vals[key]['unfix'])
                
        # print('unfix attr val: ', self.unfix_attr_vals, 'fix attr val: ', self.fix_attr_vals)
        # self.pprint()
        
    # def pprint(self):
    #     print(list(self.parse_file()))
        # print(cnt, '-->', [value for value in self._get_data_from_line(row)])
        # printrows
    

def is_digit(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
    
sheet_names = {
    'Нержавейка': 'нержавейка',
    'Лестничные': 'лестничный',
    'Оцинковка': 'хол. цинк'
}