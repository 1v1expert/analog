"""
Описание основных моделей проекта
"""
import logging
import time
import traceback
from itertools import chain
from itertools import groupby
from typing import List, Mapping, Optional

from django.contrib.auth.models import User
from django.contrib.postgres import fields as pgfields
from django.db import models
from django.db.models import F, Func, QuerySet

from catalog.choices import HARD, PRICE, RECALCULATION, RELATION, SOFT, TYPES, TYPES_FILE, UNITS
from catalog.exceptions import AnalogNotFound
from catalog.managers import CoreModelManager

logger = logging.getLogger("analog")


class Base(models.Model):
    """
    Абстрактная базовая модель
    """
    # uid = models.UUIDField(verbose_name="Идентификатор", primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Когда создано")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Кем создано", editable=False, related_name="+")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Когда обновлено")
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Кем обновлено", editable=False, related_name="+")
    is_public = models.BooleanField("Опубликовано?", default=True)
    deleted = models.BooleanField("В архиве?", default=False, editable=False)
    # rev = models.CharField("Ревизия", default='1-{0}'.format(uuid.uuid4()), max_length=38, editable=False)
    # json-delta пакет для работы с разностью в json; json_patch - функция пакета для применения изменений.

    objects = CoreModelManager()

    def delete(self, *args, **kwargs):
        # Achtung! not deleting - hiding!
        models.signals.pre_delete.send(sender=self.__class__, instance=self)
        self.deleted = True
        self.save(update_fields=('deleted',))
        models.signals.post_delete.send(sender=self.__class__, instance=self)
        
    class Meta:
        abstract = True
        verbose_name = "Базовая модель "
        verbose_name_plural = "Базовые модели"


class Manufacturer(Base):
    """
    Модель производителя товаров
    """
    title = models.CharField(verbose_name='Наименование', max_length=255)
    short_title = models.CharField(verbose_name='Краткое наименование', max_length=255, blank=True)
    is_tried = models.BooleanField(verbose_name='Проверенный', default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"


class Category(Base):
    """
    Модель класса товаров
    """
    parent = models.ForeignKey('self', on_delete=models.PROTECT, verbose_name="Родительский класс", related_name='childs', blank=True, null=True)
    childs = None
    title = models.CharField(max_length=255, verbose_name='Наименование')
    short_title = models.CharField(max_length=255, verbose_name='Краткое наименование', blank=True)
    attributes = models.ManyToManyField('Attribute', blank=True, verbose_name="Атрибуты")

    def getAttributes(self):
        if not self.childs:
            return []
        attrs = []
        for subcat in self.childs.all():
            _attrs = subcat.attributes if subcat.attributes else []
            diff = set(attrs) - set(_attrs)
            attrs = attrs + list(diff)
        return attrs

    def __str__(self):
        text = ""
        if self.parent:
            text += self.parent.short_title if self.parent.short_title else self.parent.title
            text += ' -> '
        text += self.title
        return text

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"


class Attribute(Base):
    """
    Модель атрибута товара
    """
    
    title = models.CharField(max_length=255, verbose_name='Наименование')
    type = models.CharField(max_length=13, choices=TYPES, verbose_name="Тип")
    unit = models.CharField(max_length=5, choices=UNITS, verbose_name="Единицы измерения", blank=True)
    priority = models.PositiveSmallIntegerField(verbose_name='Приоритет')
    is_fixed = models.BooleanField(verbose_name='Fixed attribute?', default=False)
    
    def __str__(self):
        return '{}({})'.format(self.title, self.type)

    class Meta:
        verbose_name = "Атрибут"
        verbose_name_plural = "Атрибуты"


class FixedValue(Base):
    """
    Модель фиксированного значения атрибута
    """
    title = models.CharField(max_length=255, verbose_name='Значение')
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT, verbose_name="Атрибут",
                                  related_name="fixed_value")
    # image = models.ImageField(upload_to='images', null=True, max_length=100, verbose_name='Изображение')

    def __str__(self):
        return '{}, title: {}, attribute: {}, type: {}'.format(self._meta.model, self.title, self.attribute.title,
                                                               self.attribute.type)

    class Meta:
        verbose_name = "Фикс значение"
        verbose_name_plural = "Фикс значения"

    
class AttributeValue(Base):
    value = models.ForeignKey(FixedValue, on_delete=models.PROTECT, verbose_name="Фиксированное значение атрибута", null=True)
    un_value = models.FloatField(verbose_name="Нефиксированное значение атрибута", null=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT, verbose_name="Атрибут")
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        
        if self.is_fixed and self.un_value is not None:
            raise Exception('Values ist can be used')
            
        super(AttributeValue, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                         update_fields=update_fields)
    
    @property
    def is_fixed(self):
        return self.attribute.is_fixed
    
    class Meta:
        verbose_name = "Значение атрибута"
        verbose_name_plural = "Значения атрибутов"


class Product(Base):
    """
    Модель товара
    """
    title = models.CharField(max_length=255, verbose_name='Наименование')
    formalized_title = models.CharField(max_length=255, null=True, verbose_name='Формализованное наименование')
    
    article = models.CharField(max_length=255, verbose_name='Артикул')
    additional_article = models.CharField(max_length=255, default="", blank=True, verbose_name='Доп. артикул')
    series = models.CharField(max_length=255, default="", blank=True, verbose_name='Серия')
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 verbose_name="Класс", related_name='products', limit_choices_to={'parent__isnull': False})
    
    is_duplicate = models.BooleanField(verbose_name='Дубликат', default=False)
    is_tried = models.BooleanField(verbose_name='Проверенный', default=False)
    is_updated = models.BooleanField(verbose_name='Обновлённый', default=False)
    
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, verbose_name="Производитель",
                                     related_name='products')

    analogs_to = models.ManyToManyField('self', related_name='analogs_from')

    raw = pgfields.JSONField(null=True, blank=True, verbose_name="Голые данные")
    
    is_base = models.BooleanField(verbose_name='Базовый', default=False)

    is_enabled = models.BooleanField(verbose_name='Поисковый', default=False)

    priority = models.PositiveSmallIntegerField(verbose_name='Приоритет', default=0)
    
    def get_analog(self, manufacturer_to: Manufacturer) -> Optional["Product"]:
        assert manufacturer_to is not None, 'Manufacturer is None'
        logger.info(
            f'call <get_analog({manufacturer_to.title})> for product: <{self.pk}>/<{self.article}>'
        )
        
        if self.manufacturer == manufacturer_to:
            return self
        
        analogs = self.analogs_to.filter(manufacturer=manufacturer_to)
        if analogs.exists():
            analog = analogs.first()
            logger.info(f'analog is <{analog.pk}/{analog.article}>')
            return analogs.first()
        
        return self.search_analog(manufacturer_to)
    
    def search_analog(self, manufacturer_to: Manufacturer) -> Optional["Product"]:
        """ Start <AnalogSearch> process """
        logger.info(f'call <search_analog({manufacturer_to.title})> for product: <{self.pk}>/<{self.article}')
        
        search = AnalogSearch(product_from=self, manufacturer_to=manufacturer_to)
        try:
            result = search.build()
        
            if result.product is None:
                return None
            
            old_analogs = self.analogs_to.filter(manufacturer=manufacturer_to)
            if old_analogs.exists():
                self.analogs_to.remove(old_analogs)

            self.analogs_to.add(result.product)
        
            raw = self.raw or {}
            raw__analogs: dict = raw.get("analogs", {})
            raw__analogs[manufacturer_to.pk] = {
                "analog_seconds": list(result.second_dataset),
                "analog": result.product.pk
            }
            raw["analogs"] = raw__analogs
            self.raw = raw
            self.save()
        
            return result.product
    
        except AnalogNotFound:
            return None
    
        except Exception as e:
            logger.debug(f'<{e}>\n{traceback.format_exc()}')
            return None
    
    def get_info(self) -> list:
        return list(self.attributevalue_set.all())
    
    def get_full_info(self):
        return self.attributevalue_set.select_related(
            'attribute',
            'value'
        ).values(
            'attribute__pk',
            'value__title',
            'un_value',
            'attribute__is_fixed'
        )
    
    def get_attributes(self):
        return {
            attribute["attribute__pk"]: {
                key: attribute[key] for key in attribute.keys()
            } for attribute in self.get_full_info()}

    def comparison(self, analog: "Product"):
        fields = ('value__title', 'un_value', 'attribute__title', 'attribute__pk', 'product__pk')
        attributes = sorted(
            chain(
                self.attributevalue_set.all().order_by('attribute__pk').values(*fields),
                analog.attributevalue_set.all().order_by('attribute__pk').values(*fields)
            ),
            key=lambda attribute: attribute['attribute__pk']
        )
        
        return groupby(attributes, lambda x: x['attribute__pk'])
        
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ('-priority', )


class Specification(Base):
    """
    Модель спецификации предложений товаров
    """
    title = models.CharField(max_length=255, verbose_name='Наименование')
    products = models.ManyToManyField(Product, verbose_name="Товары")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Спецификация"
        verbose_name_plural = "Спецификации"

        
class GroupSubclass(Base):
    """  Модель группы товаров, объединенные подклассов и фиксированным атрибутом """
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Класс товара')
    fixed_attribute = models.ForeignKey(FixedValue, on_delete=models.SET_NULL, null=True, blank=True,
                                        verbose_name='Значение аттрибута')
    image = models.ImageField(upload_to='images', null=True, max_length=100, blank=True, verbose_name='Изображение')
    
    def __str__(self):
        return 'Группа в подклассе <{}> и фикс. атрибутом <{}>'.format(self.category, self.fixed_attribute)
    
    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class DataFile(Base):
    """
    Модель загрузки файлов
    """
    file = models.FileField(upload_to='files', verbose_name='Файл')
    type = models.CharField(max_length=13, choices=TYPES_FILE, verbose_name="Тип файла", blank=True, default=TYPES_FILE[0][0])
    
    class Meta:
        ordering = ('-updated_at', )
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"
    
    def __str__(self):
        return self.file.name
    
    def save(self, *args, **kwargs):
        super(DataFile, self).save(*args, **kwargs)


class AnalogSearch(object):
    def __init__(self, product_from: Optional[Product], manufacturer_to: Optional[Manufacturer]):
        
        # self.start_time = None
        self.left_time = None
        self.initial_product = product_from
        self.initial_product_info = {}
        self.manufacturer_to = manufacturer_to
        self.product = None
        self.first_step_products = None
        self.second_dataset = None
        
        # raise product_from is None or manufacturer_to is None
        
    def filter_by_category_and_manufacturer(self) -> QuerySet:
        return Product.objects.filter(
            category=self.initial_product.category,
            manufacturer=self.manufacturer_to
        ).values_list(
            'pk',
            flat=True
        )

    def get_full_info_from_initial_product(self) -> Mapping[str, List[AttributeValue]]:
        attributes = self.initial_product.attributevalue_set.values(
            'value',
            'un_value',
            'attribute',
            'attribute__type',
            'attribute__title',
            'attribute__is_fixed'
        ).order_by('-attribute__is_fixed')  # Attr is fixed: True, True, ..., False, False

        info = {HARD: [], SOFT: [], RELATION: [], RECALCULATION: [], PRICE: []}
        for attribute in attributes:
            info[attribute["attribute__type"]].append(attribute)
        
        return info

    def filter_by_hard_attributes(self, dataset_pk) -> QuerySet:
        middleware_pk_products = dataset_pk

        for attribute in self.initial_product_info[HARD]:
            if attribute["attribute__is_fixed"]:
                middleware_pk_products = AttributeValue.objects.select_related(
                    'attribute', 'product', 'value'
                ).filter(
                    product__pk__in=middleware_pk_products,
                    # attribute__type=HARD,
                    attribute=attribute['attribute'],
                    # attribute__is_fixed=attribute["attribute__is_fixed"],
                    value=attribute["value"],
                ).distinct('product__pk').values_list('product__pk', flat=True)
            else:
                middleware_attributes = AttributeValue.objects.select_related(
                    'attribute', 'product'
                ).filter(
                    product__pk__in=middleware_pk_products,
                    # attribute__type=HARD,
                    # attribute__is_fixed=attribute["attribute__is_fixed"],
                    attribute=attribute['attribute'],
                    # value__title=attribute["value__title"],
                    # un_value=attribute["un_value"]
                ).annotate(
                    abs_diff=Func(F('un_value') - attribute["un_value"], function='ABS')
                ).order_by('abs_diff')  # .distinct('product')  # .values_list('product__pk', flat=True)

                if middleware_attributes.exists():
                    closest_attribute = middleware_attributes.first()
                    
                    middleware_pk_products = AttributeValue.objects.select_related(
                        'attribute', 'product', 'value'
                    ).filter(
                        product__pk__in=middleware_pk_products,
                        attribute=attribute['attribute'],
                        un_value=closest_attribute.un_value,
                    ).distinct('product__pk').values_list('product__pk', flat=True)
                
                # products_pk = set()
                # for idx, unfix_attribute in enumerate(middleware_attributes):
                #     if not idx:  # first iteration
                #         closest_attribute = unfix_attribute  # = min abs_diff
                #     else:
                #         if closest_attribute.abs_diff == unfix_attribute.abs_diff:
                #             products_pk.update(closest_attribute.product.pk)
                # if len(products_pk):
                #     middleware_pk_products = Product.objects.filter(pk__in=products_pk).values_list('pk', flat=True)
                
        return middleware_pk_products
    
    def filter_by_soft_attributes(self, dataset_pk: QuerySet) -> QuerySet:
        middleware_pk_products = dataset_pk

        for attribute in self.initial_product_info[SOFT]:
            if attribute["attribute__is_fixed"]:
                products_pk: QuerySet = AttributeValue.objects.select_related(
                    'attribute', 'product', 'value'
                ).filter(
                    product__pk__in=middleware_pk_products,
                    attribute=attribute["attribute"],
                    value=attribute["value"],
                ).distinct('product').values_list('product__pk', flat=True)
        
                if products_pk.count() > 0:
                    middleware_pk_products = products_pk

            else:
                products_pk = AttributeValue.objects.select_related(
                    'attribute', 'product'
                ).filter(
                    product__pk__in=middleware_pk_products,
                    attribute=attribute['attribute'],
                ).annotate(
                    abs_diff=Func(F('un_value') - attribute["un_value"], function='ABS')
                ).order_by('abs_diff')  # .distinct('product')  # .values_list('product__pk', flat=True)
    
                set_products_pk = set()
                for idx, unfix_attribute in enumerate(products_pk):
                    if not idx:  # first iteration
                        closest_attribute = unfix_attribute  # = min abs_diff
                    else:
                        if closest_attribute.abs_diff == unfix_attribute.abs_diff:
                            set_products_pk.add(closest_attribute.product.pk)
                if len(set_products_pk):
                    middleware_pk_products = Product.objects.filter(pk__in=set_products_pk).values_list('pk', flat=True)

        return middleware_pk_products

    def build(self) -> "AnalogSearch":
        start_time = time.time()
        # logger.
        self.initial_product_info = self.get_full_info_from_initial_product()
        
        # first step
        first_dataset: QuerySet = self.filter_by_category_and_manufacturer()
        
        # second step
        second_dataset: QuerySet = self.filter_by_hard_attributes(first_dataset)

        if second_dataset.count() == 0:
            raise AnalogNotFound('Not founded')  # after hard check
        
        self.second_dataset = list(second_dataset)
        # third step
        third_dataset: QuerySet = self.filter_by_soft_attributes(second_dataset)
        
        products = Product.objects.filter(pk__in=third_dataset)

        self.product = products.first()
        self.first_step_products = products
        self.left_time = time.time() - start_time
        return self
