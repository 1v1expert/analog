"""
Описание основных моделей проекта
"""

from itertools import chain
from itertools import groupby

from django.contrib.auth.models import User
from django.contrib.postgres import fields as pgfields
from django.db import models

from catalog.choices import TYPES, TYPES_FILE, UNITS
from catalog.managers import CoreModelManager


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

    def comparison(self, analog):
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