"""
Описание основных моделей проекта
"""

from django.db import models
from django.db.models import Q
# import uuid
from django.contrib.auth.models import User

from catalog.choices import TYPES, UNITS, TYPES_FILE
from catalog.managers import CoreModelManager

from django.contrib.postgres import fields as pgfields

from itertools import chain
import mptt
from django.utils import timezone


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

    # def save(self, *args, **kwargs):
    #     if not self.uid:
    #         self.created_at = timezone.now()
    
    #     self.updated_at = timezone.now()
    #     return super(Base, self).save(*args, **kwargs)


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

mptt.register(Category, )


class Attribute(Base):
    """
    Модель атрибута товара
    """
    
    title = models.CharField(max_length=255, verbose_name='Наименование')
    type = models.CharField(max_length=13, choices=TYPES, verbose_name="Тип")
    unit = models.CharField(max_length=5, choices=UNITS, verbose_name="Единицы измерения", blank=True)
    priority = models.PositiveSmallIntegerField(verbose_name='Приоритет')
    #category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Класс", related_name='attributes', limit_choices_to={'parent__isnull': False})
    
    def __str__(self):
        return '{}({})'.format(self.title, self.type)
        # self.UNITS = UNITS
        # text = self.title
        # if self.unit:
        #     for unit in self.UNITS:
        #         if self.unit == unit[0]:
        #             text += ', ' + unit[1]
        # return text

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
    
    
class FixedAttributeValue(Base):
    """
    Модель фиксированного значения атрибута
    """
    value = models.ForeignKey(FixedValue, on_delete=models.PROTECT, verbose_name="Фиксированное значение атрибута")
    # title = models.CharField(max_length=255, verbose_name='Значение')
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT, verbose_name="Атрибут", related_name="fixed_values")
    products = models.ManyToManyField('Product', blank=True)
    is_tried = models.BooleanField(verbose_name='Проверенный', default=False)
    
    def __str__(self):
        return str(self.attribute) + ": " + self.value.title
    
    class Meta:
        verbose_name = "Значение атрибута(фикс)"
        verbose_name_plural = "Значения атрибутов(фикс)"


class UnFixedAttributeValue(Base):
    """
    Модель нефиксированного значения атрибута
    """
    value = models.FloatField(verbose_name="Нефикс значение атрибута")
    # title = models.CharField(max_length=255, verbose_name='Значение')
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT, verbose_name="Атрибут", related_name="unfixed_values")
    products = models.ManyToManyField('Product', blank=True)
    is_tried = models.BooleanField(verbose_name='Проверенный', default=False)
    
    def __str__(self):
        return '{}: {}'.format(self.attribute, self.value)
    
    class Meta:
        verbose_name = "Значение атрибута(нефикс)"
        verbose_name_plural = "Значения атрибутов(нефикс)"


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
    
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, verbose_name="Производитель", related_name='products')
    
    fixed_attrs_vals = models.ManyToManyField('FixedAttributeValue', verbose_name="Фикс атрибуты")
    unfixed_attrs_vals = models.ManyToManyField('UnFixedAttributeValue', verbose_name="Нефикс атрибуты")

    raw = pgfields.JSONField(null=True, blank=True, verbose_name="Голые данные")
    
    is_base = models.BooleanField(verbose_name='Базовый', default=False)

    is_enabled = models.BooleanField(verbose_name='Поисковый', default=False)

    priority = models.PositiveSmallIntegerField(verbose_name='Приоритет', default=0)
    
    def get_attributes(self):
        return '{} {}'.format(self.fixed_attrs_vals.all(), self.unfixed_attrs_vals.all())
    
    def get_info(self):
        # return Q(self.fixed_attrs_vals.all()) | Q(self.unfixed_attrs_vals.all())
        return chain(self.fixed_attrs_vals.all(), self.unfixed_attrs_vals.all())
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ('-priority', )


# class ProductProperty(Base):
#     """
#     Модель, связующая товар и атрибут и его значение
#     """
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)


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
    fixed_attribute = models.ForeignKey(FixedValue, on_delete=models.PROTECT, verbose_name='Значение аттрибута')
    image = models.ImageField(upload_to='images', null=True, max_length=100, verbose_name='Изображение')
    
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