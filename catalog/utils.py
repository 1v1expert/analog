import time

from catalog.exceptions import NotFoundException
from catalog.models import Manufacturer, Product, UnFixedAttributeValue, FixedValue, FixedAttributeValue
from catalog.choices import HARD, SOFT, RELATION, RECALCULATION, PRICE


class AnalogSearch(object):
    def __init__(self, product_from: Product = None, manufacturer_to: Manufacturer = None):
        self.initial_product = product_from
        self.initial_product_info = {}
        self.manufacturer_to = manufacturer_to
        self.products_found = []
        
    def find_products_with_category(self):
        return Product.objects.filter(category=self.initial_product.category)
    
    @staticmethod
    def _get_hrd_fix_attributes(products):
        return FixedAttributeValue.objects.filter(product__in=products, attribute__type=HARD)
    
    @staticmethod
    def _get_hrd_unfix_attributes(products):
        return UnFixedAttributeValue.objects.filter(product__in=products, attribute__type=HARD)

    def get_full_info_from_initial_product(self):
        info = {HARD: [], SOFT: [], RELATION: [], RECALCULATION: [], PRICE: []}
        for attr in self.initial_product.fixed_attrs_vals.values_list('value__title',
                                                                      'attribute__type',
                                                                      'attribute__title'):
            info[attr[1]].append({'value': attr[0],
                                  'attribute': attr[2],
                                  'type': 'fix'
                                  })
    
        for attr in self.initial_product.unfixed_attrs_vals.values_list('value', 'attribute__type', 'attribute__title'):
            info[attr[1]].append({'value': attr[0],
                                  'attribute': attr[2],
                                  'type': 'unfix'
                                  })
        return info
    
    def find_unfix_value(self, values_list, value, method='nearest'):
        if method == 'min':
            value = min(values_list, key=lambda x: x)
        elif method == 'max':
            value = max(values_list, key=lambda x: x)
        else:  # method = 'nearest
            # print(values_list, step_attr.value)
            value = min(values_list, key=lambda x: abs(x - value))
        return value
    
    def find_in_hrd_attributes(self, fix, unfix):
        middleware_pk_products = [] #
        for hrd in self.initial_product_info[HARD]:
            if hrd['type'] == 'unfix':
                pass
        
    def build(self):
        self.initial_product_info = self.get_full_info_from_initial_product()
        
        # first step
        products_with_category = self.find_products_with_category()
        
        fix_attrs_values_list = self._get_hrd_fix_attributes(products_with_category)\
            .values_list('product__pk', 'value__title', 'attribute__type', 'attribute__title')
        unfix_attrs_values_list = self._get_hrd_unfix_attributes(products_with_category)\
            .values_list('product__pk', 'value', 'attribute__type', 'attribute__title')
        
        
    def smart_search(self, products):
        pass
    
    
# if __name__ == '__main__':
#     north_aurora_product = Product.objects.filter(
#         category__title__iexact='Прямая секция', manufacturer=Manufacturer.objects.get(title='Северная Аврора')).first()
#     fixed_attrs = north_aurora_product.fixed_attrs_vals.values_list('value__title', 'attribute__type', 'attribute__title')
#     unfixed_attrs = north_aurora_product.unfixed_attrs_vals.values_list('value', 'attribute__type', 'attribute__title')
#     make_search = AnalogSearch(product_from=north_aurora_product, manufacturer_to=Manufacturer.objects.first())
#
#     print(fixed_attrs, unfixed_attrs)
#     find_products = make_search.find_products_with_category()
#     f_fixed_attrs = FixedAttributeValue.objects.filter(product__in=find_products)
#     print(f_fixed_attrs.count())
#     f_fixed_attrs_values = f_fixed_attrs.values_list('product__pk', 'value__title', 'attribute__type', 'attribute__title')
#     print(f_fixed_attrs_values)
    # f_unfixed_attrs = north_aurora_product.unfixed_attrs_vals.values_list('value', 'attribute__type', 'attribute__title')
    
    
class SearchProducts(object):
    def __init__(self, form=None, product=None, manufacturer_to=None):
        
        # self.request = request
        self.form = form
        self.product = product
        # self.manufacturer_to = form.cleaned_data['manufacturer_to']
        self.manufacturer_from = None
        self.manufacturer_to = manufacturer_to
        
        if manufacturer_to is None:
            self.manufacturer_to = form.cleaned_data['manufacturer_to']
        
        if self.product is None:
            self.article = form.cleaned_data['article']
        else:
            self.article = product
        # self.product = product
        self.founded_products = None
        self.start_time = time.time()
        self.lead_time = 0
        self.error = False
    
    @staticmethod
    def finding_the_closest_attribute_value(all_attr, step_attr, method, types='sft'):
        
        values_list = []
        for attr in all_attr:
            try:
                value = attr.unfixed_attrs_vals.get(attribute__type=types,
                                                    attribute__title=step_attr.attribute.title).value
            except UnFixedAttributeValue.DoesNotExist:
                value = 0
            values_list.append(value)
        
        # print(values_list)
        
        if method == 'min':
            value = min(values_list, key=lambda x: x)
        elif method == 'max':
            value = max(values_list, key=lambda x: x)
        else:  # method = 'nearest
            # print(values_list, step_attr.value)
            value = min(values_list, key=lambda x: abs(x - step_attr.value))
        return value
    
    def smart_attribute_search(self, default=True):
        method = 'nearest'
        all_fix_attributes = self.product.fixed_attrs_vals.all()
        all_unfix_attributes = self.product.unfixed_attrs_vals.all()
        # hrd attr
        hrd = 'hrd'
        hrd_fix_attributes = all_fix_attributes.filter(
            attribute__type=hrd)
        hrd_unfix_attributes = all_unfix_attributes.filter(
            attribute__type=hrd)  # self.product.unfixed_attrs_vals.filter(attribute__type=hrd)
        for hrd_fix_attr in hrd_fix_attributes:

            if default:
                value = hrd_fix_attr.value.pk
            else:
                value = self.form.cleaned_data['extra_field_fix{}'.format(hrd_fix_attr.pk)]

            self.founded_products = self.founded_products.filter(
                fixed_attrs_vals__value__pk=value,
                fixed_attrs_vals__attribute=hrd_fix_attr.attribute
            )

        if not self.founded_products.exists():
            return
        
        for hrd_unfix_attr in hrd_unfix_attributes:
            if not default:
                method = self.form.cleaned_data['extra_field_unfix{}'.format(hrd_unfix_attr.pk)]
            value = self.finding_the_closest_attribute_value(self.founded_products, hrd_unfix_attr, method, types=hrd)

            self.founded_products = self.founded_products.filter(
                unfixed_attrs_vals__value=value,
                unfixed_attrs_vals__attribute=hrd_unfix_attr.attribute
            )
            if not self.founded_products.exists():
                raise NotFoundException(
                    'Not found products after hrd cycle filtering'
                )
        # attrs_vals__attribute=attribute.attribute)
        
        # print('Count after HRD search prdcts-> ', self.founded_products.count())
        # if not self.founded_products.exists():
            # return
        # middle_results = self.founded_products
        # sft attr
        sft = 'sft'
        sft_fix_attributes = all_fix_attributes.filter(
            attribute__type=sft)  # self.product.fixed_attrs_vals.filter(attribute__type=sft)
        # print(sft_fix_attributes)
        sft_unfix_attributes = all_unfix_attributes.filter(
            attribute__type=sft)  # self.product.unfixed_attrs_vals.filter(attribute__type=sft)
        for sft_fix_attr in sft_fix_attributes:
            if default:
                value = sft_fix_attr.value.pk
            else:
                value = self.form.cleaned_data['extra_field_fix{}'.format(sft_fix_attr.pk)]
            # print(value)
            middle_results = self.founded_products.filter(fixed_attrs_vals__value__pk=value,
                                                          # attrs_vals__title=attribute.title,
                                                          fixed_attrs_vals__attribute=sft_fix_attr.attribute)
            count = middle_results.count()
            if count > 1:
                self.founded_products = middle_results
            if count == 1:
                self.founded_products = middle_results
                return
        # print('Count after SFT FIX search prdcts-> ', self.founded_products.count())
        # middle_results = self.founded_products
        for sft_unfix_attr in sft_unfix_attributes:
            if not default:
                method = self.form.cleaned_data['extra_field_unfix{}'.format(sft_unfix_attr.pk)]
            value = self.finding_the_closest_attribute_value(self.founded_products, sft_unfix_attr, method, types=sft)
            # print(value, sft_unfix_attr.value, type(value), type(sft_unfix_attr.value))
            middle_results = self.founded_products.filter(unfixed_attrs_vals__value=value,
                                                          # attrs_vals__title=attribute.title,
                                                          unfixed_attrs_vals__attribute=sft_unfix_attr.attribute)
            count = middle_results.count()
            if count > 1:
                self.founded_products = middle_results
            if count == 1:
                self.founded_products = middle_results
                return
        
        # rcl attr
        rcl = 'rcl'
        rcl_unfix_attributes = all_unfix_attributes.filter(
            attribute__type=rcl)  # self.product.unfixed_attrs_vals.filter(attribute__type=rcl)
        # print(rcl_unfix_attributes)
        # print('Count after SFT search prdcts-> ', self.founded_products.count())
        # middle_results = self.founded_products
        for rcl_unfix_attr in rcl_unfix_attributes:
            if not default:
                method = self.form.cleaned_data['extra_field_unfix{}'.format(rcl_unfix_attr.pk)]
            value = self.finding_the_closest_attribute_value(self.founded_products, rcl_unfix_attr, method, types=rcl)
            # print(value, rcl_unfix_attr.value, type(value), type(rcl_unfix_attr.value))
            middle_results = self.founded_products.filter(unfixed_attrs_vals__value=value,
                                                          # attrs_vals__title=attribute.title,
                                                          unfixed_attrs_vals__attribute=rcl_unfix_attr.attribute)
            count = middle_results.count()
            if count > 1:
                self.founded_products = middle_results
            if count == 1:
                self.founded_products = middle_results
                return
    
    def check_product(self):
        if self.form is not None:
            self.manufacturer_from = self.form.cleaned_data.get('manufacturer_from')
            if self.manufacturer_from:
                self.product = Product.objects\
                    .filter(article=self.article, manufacturer=self.manufacturer_from)\
                    .select_related('manufacturer', 'category').first()
        else:
            self.product = Product.objects.filter(article=self.article) \
                .select_related('manufacturer', 'category').first()
        
        if not self.product:
            self.error = True

        return not self.error
    
    def global_search(self, default=True):
        if self.product is None:
            checked = self.check_product()
            if not checked:
                return self
        # if not self.check_product():
        #     return self
        
        if self.product.manufacturer == self.manufacturer_to:
            self.founded_products = Product.objects.filter(pk=self.product.pk)
            return self
        
        self.founded_products = Product.objects.filter(manufacturer=self.manufacturer_to,
                                                       category=self.product.category).prefetch_related(
            'fixed_attrs_vals', 'unfixed_attrs_vals')
        # print(self.founded_products.count())
        if self.founded_products.exists():
            self.smart_attribute_search(default=default)
        self.lead_time = time.time() - self.start_time
        # print(self.founded_products.count())
        return self

