import time
from typing import Optional

from catalog.choices import HARD, PRICE, RECALCULATION, RELATION, SOFT
from catalog.exceptions import AnalogNotFound
from catalog.models import Manufacturer, Product, AttributeValue


class AnalogSearch(object):
    def __init__(self, product_from: Optional[Product] = None, manufacturer_to: Optional[Manufacturer] = None):
        
        self.start_time = time.time()
        self.left_time = None
        self.initial_product = product_from
        self.initial_product_info = {}
        self.manufacturer_to = manufacturer_to
        self.product = None
        self.first_step_products = None
        
        # raise product_from is None or manufacturer_to is None
        
    def find_products_with_category(self):
        return Product.objects.filter(category=self.initial_product.category, manufacturer=self.manufacturer_to)

    def get_full_info_from_initial_product(self):
        attributes = self.initial_product.attributevalue_set.values(
            'value__title',
            'un_value',
            'attribute__type',
            'attribute__title',
            'attribute__is_fixed'
        )
        # return {attribute['attribute__title']: attribute for attribute in attributes}
        info = {HARD: [], SOFT: [], RELATION: [], RECALCULATION: [], PRICE: []}
        for attribute in attributes:
            info[attribute["attribute__type"]].append(attribute)
        # for attr in self.initial_product.fixed_attrs_vals.values_list('value__title',
        #                                                               'attribute__type',
        #                                                               'attribute__title'):
        #     info[attr[1]].append({'value': attr[0],
        #                           'attribute': attr[2],
        #                           'type': 'fix'
        #                           })
        #
        # for attr in self.initial_product.unfixed_attrs_vals.values_list('value', 'attribute__type', 'attribute__title'):
        #     info[attr[1]].append({'value': attr[0],
        #                           'attribute': attr[2],
        #                           'type': 'unfix'
        #                           })
        return info
    
    def find_unfix_value(self, values_list, value, method='nearest'):
        # value = (119444, 500.0, 'hrd', 'ширина')
        # value_list <QuerySet [(51903, 0.0, 'hrd', 'ширина доп.'), (51904, 0.0, 'hrd', 'ширина доп.'), (51905, 0.0, 'hrd', 'ширина доп.') # noqa
        if method == 'min':
            values = min(values_list, key=lambda x: x[1])
        elif method == 'max':
            values = max(values_list, key=lambda x: x[1])
        else:  # method = 'nearest
            # print(values_list, step_attr.value)
            values = min(values_list, key=lambda x: abs(x[1] - value))
        
        # print(values, value)
        pks = {val[0] if values[1] == val[1] else None for val in values_list}
        if None in pks: pks.remove(None)
        # print(pks)
        return pks

    def find_fix_value(self, values_list, value):
        # print(value)
        pks = {val[0] if value == val[1] else None for val in values_list}
        if None in pks: pks.remove(None)
        return pks
    
    def find_by_hard_attributes(self, query):
        middleware_pk_products = []
        for i, attribute in enumerate(self.initial_product_info[HARD]):
            if i == 0:
                middleware_pk_products = list(AttributeValue.objects.filter(
                    product__in=query,
                    attribute__type=HARD,
                    attribute__is_fixed=attribute["attribute__is_fixed"],
                    value__title=attribute["value__title"],
                    un_value=attribute["un_value"]
                ).distinct('product__pk').values_list('product__pk', flat=True))
            
            else:
                middleware_pk_products = list(AttributeValue.objects.filter(
                    product__pk__in=middleware_pk_products,
                    attribute__type=HARD,
                    attribute__is_fixed=attribute["attribute__is_fixed"],
                    value__title=attribute["value__title"],
                    un_value=attribute["un_value"]
                ).distinct('product__pk').values_list('product__pk', flat=True))
        
        return middleware_pk_products
    
    def find_by_soft_attributes(self, query_pk):
        pass
        
    def build(self):
        self.initial_product_info = self.get_full_info_from_initial_product()
        
        # first step
        founded_first = self.find_products_with_category()
        
        # fix_hrd_attrs_values_list = self._get_hrd_fix_attributes(founded_first)\
        #     .values_list('product__pk', 'value__title', 'attribute__type', 'attribute__title')
        # unfix_hrd_attrs_values_list = self._get_hrd_unfix_attributes(founded_first)\
        #     .values_list('product__pk', 'value', 'attribute__type', 'attribute__title')
        
        # second step
        second_founded = self.find_by_hard_attributes(founded_first)
        
        
        if not len(second_founded):
            raise Exception('Not founded')
        # third step
        products = Product.objects.filter(pk__in=second_founded)
        # fix_soft_attrs_values_list = self._get_soft_fix_attributes(products)\
        #     .values_list('product__pk', 'value__title', 'attribute__type', 'attribute__title')
        # unfix_soft_attrs_values_list = self._get_soft_unfix_attributes(products)\
        #     .values_list('product__pk', 'value', 'attribute__type', 'attribute__title')
        #
        # third_founded = self.find_by_attributes(fix_soft_attrs_values_list, unfix_soft_attrs_values_list)
        # if not len(third_founded):
        #     raise Exception('Not founded')
        #
        # # fourth second
        # products = Product.objects.filter(pk__in=third_founded)
        self.product = products.first()
        self.first_step_products = products
        self.left_time = time.time() - self.start_time
        return self
        
        
    def smart_search(self, products):
        pass


# if __name__ == '__main__':
#     north_aurora_product = Product.objects.filter(
#         category__title__iexact='Прямая секция', manufacturer=Manufacturer.objects.get(title='Северная Аврора')).first()
#
#     eae_manufacturer = Manufacturer.objects.get(title='EAE')
#
#     manager = AnalogSearch(product_from=north_aurora_product, manufacturer_to=eae_manufacturer)
#     manager.build()



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
                raise AnalogNotFound('Аналог не найден'
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


# if __name__ == '__main__':
#     north_aurora_product = Product.objects.filter(
#         category__title__iexact='Прямая секция', manufacturer=Manufacturer.objects.get(title='Северная Аврора')).first()
#
#     eae_manufacturer = Manufacturer.objects.get(title='EAE')
#     manager = SearchProducts(product=north_aurora_product, manufacturer_to=eae_manufacturer)
#     manager.global_search()
