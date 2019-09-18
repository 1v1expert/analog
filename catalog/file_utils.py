import openpyxl
from openpyxl.utils.exceptions import InvalidFileException
from collections import OrderedDict

from catalog.choices import *
from catalog.models import *
from catalog.internal.neural_network import NeuralNetworkOption2

from app.models import MainLog

from django.contrib import messages
from django.contrib.auth import models as auth_md
from django.db import models
from django.db.models.functions import Lower

import time

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

    def __init__(self, data, start_time=None):
        if start_time is None:
            self.start_time = time.time()
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
        
        for opt in range(7, len(self.attributes) + 4):
            self.unique_type_attributes.add(self.attributes[opt])
            self.unique_value_attributes.add(self.options[opt])
        
        for count, line in enumerate(self.body):
            if count % 100 == 0:
                logger.debug('Line #{}'.format(count))
                # messages.add_message(request, messages.INFO, 'Success processed {} lines'.format(count))
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
                        "value": float(line[key].replace(',', '.')) if is_digit(line[key].replace(',', '.')) else line[key].lstrip().rstrip(),
                        "is_digit": is_digit(line[key].replace(',', '.'))
                        })
            structured_product.update({
                STRUCTURE_PRODUCT[7][1]: attributes
            })
        
            is_valid_data = self.check_exists_types(structured_product)
            if isinstance(is_valid_data, str):
                logger.debug('{}\n reason: {}'.format(structured_product, is_valid_data))
                return False, is_valid_data
            else:
                self.products.append(is_valid_data)
        logger.debug('Check correct and finish, start creating products')
        # messages.add_message(request, messages.SUCCESS, 'Check correct and finish, start create products')
        self.create_products(request)
        MainLog(user=request.user, message='Processing success in {}  seconds'.format(time.time()-self.start_time)).save()
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
        self.only_parse = only_parse
        self.c_lines = 0
        
        self.user = user if user is not None else auth_md.User.objects.get(is_staff=True, username='admin')
        
        self.manufacturer = Manufacturer.objects.get(title='КОКС')
        self.hrd_attributes = FixedValue.objects.filter(attribute__type='hrd').annotate(title_lower=Lower('title'))\
            .only('title').values_list('title_lower', flat=True).distinct()
        
        # self.formalized_title = None
        self.products = []
        self.articles = set()
        self.doubles_article = []
        # self.fix_attr_vals = {}
        # self.unfix_attr_vals = {}
        self.attr_vals = {}
        
        self.network = NeuralNetworkOption2(loadmodel=True)
        
    # @staticmethod
    # def _get_data_from_line(row):
    #     for cell in row:
    #         yield str(cell.value)
    #
    def create_products(self, article, title, formalized_title, category, additional_article="", raw=None):
        product = Product(article=article,
                          additional_article=additional_article,
                          manufacturer=self.manufacturer,
                          title=title,
                          formalized_title=formalized_title,
                          category=category,
                          created_by=self.user,
                          updated_by=self.user)
        if raw is not None:
            product.raw = raw
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
    def _get_category_from_product(required_samples, first_sign=None):
        # -- search category from category product
        products = Product.objects.filter(is_tried=True)
        if first_sign is not None:
            products = products.filter(title__icontains=first_sign)

        preparatory = products
        for word_sample in required_samples:
            # preparatory = products
            selection = products.filter(title__icontains=word_sample)
            if selection.count() > 1:
                products = selection
            elif selection.count() == 1:
                preparatory = selection
                break
            elif not selection.count():
                continue
            
            if selection.count() < preparatory.count():
                preparatory = selection
            
        product = preparatory.first()
        if product:
            return product.category
        else:
            return None
        # -- end search from category product
    
    def _get_category_with_neural_network(self, title):
        name_category = self.network.predict(title, 1000)
        return Category.objects.filter(title=name_category).first()
       
    @staticmethod
    def _get_category_from_categories(required_samples):
        from catalog.dictionaries import vocabulary
    
        for word in required_samples:
            for analogues in vocabulary:
                if word in analogues:
                    for analog in analogues:
                        categories = Category.objects.filter(title__icontains=analog)
                        if categories.count():
                            logger.debug('found word in vc {}, categories: {}'.format(
                                analogues,
                                categories.values_list('title', flat=True)))
                            return categories.first()
        
            categories = Category.objects.filter(title__icontains=word)
            if categories.count():
                logger.debug(categories.values_list('title', flat=True))
                return categories.first()
            
        return None
    
    def _get_categories(self, title):
        result = re.findall(r'\w+\d+', title)  # choose sizes
        result2 = re.findall(r'\w+', title)  # split the line word or numbers
        result3 = title.split(' ')  # full split
        first_sing = None  # sing '°'
        
        required_samples = list()
        for word in result2:
            if len(word) <= 4:
                continue
            coincided = False
            for size in result:
                if size in word:
                    coincided = True
                    break
            if not coincided:
                required_samples.append(word)
        
        for word in result3:
            if '°' in word:
                first_sing = word
        
        logger.debug('result {}, result2: {}, result3: {}\n Required samples: {}'.format(result, result2, result3, required_samples))
        
        return self._get_category_from_categories(required_samples), \
               self._get_category_from_product(required_samples, first_sign=first_sing), \
               self._get_category_with_neural_network(title)
        # not a line world list !! Attention !
        
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
    
    def line_processing(self, line, name_sheet=None):
        if not name_sheet:
            name_sheet = self.sheets[0]
        additional_article = line[0]
        article = line[1]
        title = line[2]
        price = line[3].replace(',', '.')
        formalized_title = self.network.remove_stop_words(title)
        
        if not article.strip() or article == 'None':
            return
        
        self.c_lines += 1  # counter lines
        
        # check_doubles
        if article in self.articles:
            self.doubles_article.append(article)
            return
        self.articles.add(article)
        
        category_from_categories, category_from_product, category_from_neural = self._get_categories(title)
        category = category_from_neural
        # if category_from_categories:
        #     category = category_from_categories
        
        if category:
            self.create_products(article, title, formalized_title, category, additional_article=additional_article,
                                 raw={'category_from_categories': str(category_from_categories),
                                      'category_from_product': str(category_from_product)})
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
    

class IEKDocumentReader(KOKSDocumentReader):
    def __init__(self, path=None, workbook=None, only_parse=True, user=None):
        super().__init__(path=path, workbook=workbook, only_parse=only_parse, user=user)
        self.manufacturer = Manufacturer.objects.get(title='IEK')

    def line_processing(self, line, name_sheet=None):
        article = line[0]
        title = line[1]
        price = line[9]
        formalized_title = self.network.remove_stop_words(title)
        
        # if not title:
        #     return

        if not article.strip() or title.strip().lower() == 'none' or not title:
            return

        self.c_lines += 1  # counter lines

        # check_doubles
        if article in self.articles:
            self.doubles_article.append(article)
            return
        self.articles.add(article)
        
        category_from_categories, category_from_product, category_from_neural = self._get_categories(title)
        category = category_from_neural
        
        if category:
            self.create_products(article, title, formalized_title, category,
                                 raw={'category_from_categories': str(category_from_categories),
                                      'category_from_product': str(category_from_product),
                                      'raw_line': str(line)})
            self._finding_an_fix_attribute(title, article)
            if is_digit(price):  # create price attr
                attribute = Attribute.objects.get(title='цена')
                self._create_attribute(article, float(price), attribute, fixed=False)


class GeneralDocumentReader(KOKSDocumentReader):
    
    def line_processing(self, line, name_sheet=None):
        title = line[0].strip()
        article = line[1].strip()
        additional_article = line[2].strip() if line[2] is not 'None' else ''
        category_name = line[3].strip()
        species = line[4] if line[4] is not 'None' else ''
        covering = line[5] if line[5] is not 'None' else ''
        price = line[6].strip() if line[6] is not 'None' else ''
        length = line[7].strip() if line[7] is not 'None' else ''
        depth = line[8].strip() if line[8] is not 'None' else ''
        board_height = line[9].strip() if line[9] is not 'None' else ''
        width = line[10].strip() if line[10] is not 'None' else ''

        formalized_title = self.network.remove_stop_words(title)
        
        if not article.strip() or title.strip().lower() == 'none' or not title:
            return
        
        self.c_lines += 1  # counter lines
        
        # check_doubles
        if article in self.articles:
            self.doubles_article.append(article)
            return
        self.articles.add(article)
        print(title, article, species, covering)
        category = Category.objects.get(title=category_name)
        self.create_products(article, title, formalized_title, category, additional_article=additional_article)
        
        if is_digit(price) and price:  # create price attr
            attribute = Attribute.objects.get(title='цена')
            self._create_attribute(article, float(price), attribute, fixed=False)
        
        if covering:
            value = FixedValue.objects.get(title=covering)
            attribute = Attribute.objects.get(title='покрытие')
            self._create_attribute(article, value, attribute, fixed=True)

        if species:
            value = FixedValue.objects.get(title=species)
            attribute = Attribute.objects.get(title='вид')
            self._create_attribute(article, value, attribute, fixed=True)
        
        if is_digit(length) and length:
            attribute = Attribute.objects.get(title='длина')
            self._create_attribute(article, float(length), attribute, fixed=False)
        
        if is_digit(depth) and depth:
            attribute = Attribute.objects.get(title='толщина')
            self._create_attribute(article, float(depth), attribute, fixed=False)
            
        if is_digit(board_height) and board_height:
            attribute = Attribute.objects.get(title='высота борта')
            self._create_attribute(article, float(board_height), attribute, fixed=False)
        
        if is_digit(width) and width:
            attribute = Attribute.objects.get(title='ширина')
            self._create_attribute(article, float(width), attribute, fixed=False)

    def parse_file(self):
        for name_list in self.sheets:
            self.manufacturer = Manufacturer.objects.get(title=name_list)
            logger.debug('Sheet {}'.format(name_list))
            self.sheet = self.workbook.get_sheet_by_name(name_list)
            for i, line in enumerate(self.read_sheet()):
                if not i:
                    continue
                self.line_processing(line)
    
        self._create_attributes_and_products()


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
