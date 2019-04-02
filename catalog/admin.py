from django.contrib import admin
from .models import Category, Product, Manufacturer, Attribute, AttributeValue, Specification, DataFile
from django.contrib import messages
import json


def mark_as_published(modeladmin, request, queryset):
    queryset.update(is_public=True)
mark_as_published.short_description = u"Опубликовать"

def mark_as_unpublished(modeladmin, request, queryset):
    queryset.update(is_public=False)
mark_as_unpublished.short_description = u"Снять с публикации"



class BaseAdmin(admin.ModelAdmin):

    list_display = ['title', 'id','is_public', 'deleted','created_at','created_by','updated_at','updated_by']
    save_on_top = True
    actions = [mark_as_published, mark_as_unpublished]
    list_filter = ['is_public', 'deleted','created_at','updated_at']
    search_fields = ['id', 'title']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not change:
                instance.created_by = request.user
            instance.updated_by = request.user
            instance.save()


class SubCatValInline(admin.TabularInline):
    model = Category


class CategoryAdmin(BaseAdmin):
    autocomplete_fields = ['parent']
    inlines=[SubCatValInline]


class AttrAdmin(BaseAdmin):
    list_display=['title', 'unit', 'id', 'type', 'priority', 'category', 'is_public', 'deleted']
    autocomplete_fields = ['category']


class AttrValAdmin(BaseAdmin):
    list_display=['title', 'attribute', 'id', 'is_public', 'deleted']
    
    autocomplete_fields = ['attribute']
    exclude= ('products',)
    
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "attribute":
    #         print(json.dumps(kwargs, indent=2))
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

from django.contrib.admin.views.main import ChangeList
from .models import Product
from .forms import ProductChangeListForm
class ProductChangeList(ChangeList):
    def __init__(self, request, model, list_display, list_display_links,
                 list_filter, date_hierarchy, search_fields, list_select_related,
                 list_per_page, list_max_show_all, list_editable, model_admin, sortable_by):
        super(ProductChangeList, self).__init__(request, model, list_display, list_display_links,
                 list_filter, date_hierarchy, search_fields, list_select_related,
                 list_per_page, list_max_show_all, list_editable, model_admin, sortable_by)
    
        # these need to be defined here, and not in MovieAdmin
        self.list_display=['title', 'article', 'manufacturer', 'attrs_vals', 'category','is_public', 'deleted']
        self.list_display_links = ['attrs_vals']
        # self.list_editable = ['genre']


# class ProductAdmin(admin.ModelAdmin):
#


class ProductAdmin(BaseAdmin):
    list_display = ['title', 'article', 'manufacturer', 'get_attrs_vals', 'category', 'is_public', 'deleted']
    # inlines = [PropertiesInline]
    #filter_horizontal = ['attrs_vals']
    autocomplete_fields = ['category', 'manufacturer',]

    def get_attrs_vals(self, obj):
        return "; ".join(['{}: {}'.format(p.attribute.title, p.title) for p in obj.attrs_vals.all()])

    # def get_changelist(self, request, **kwargs):
    #     return ProductChangeList
    #
    # def get_changelist_form(self, request, **kwargs):
    #     return ProductChangeListForm
    # exclude = ('attrs_vals', )

# class ListingAdmin(BaseAdmin):
#     actions = None
#     search_fields = ['=user__username', ]
#     fieldsets = [
#         (None, {'fields':()}),
#         ]

#     def __init__(self, *args, **kwargs):
#         super(LogEntryAdmin, self).__init__(*args, **kwargs)
#         self.list_display_links = (None, )
from .utils import XLSDocumentReader, ProcessingUploadData
class FileUploadAdmin(admin.ModelAdmin):
    actions = ['process_file']
    list_display = ['file']

    def process_file(self, request, queryset):
        print(request, vars(queryset[0].file), queryset)
        for qq in queryset:
            created, error = ProcessingUploadData(
                XLSDocumentReader(path=qq.file.name).parse_file()
            ).get_structured_data(request)
            if created:
                messages.add_message(request, messages.SUCCESS, 'Данные успешно загружены из {} файла в БД'.format(qq.file.name))
            else:
                messages.add_message(request, messages.ERROR, error)
    process_file.short_description = u'Импортировать данные'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()
    
    #autocomplete_fields = ['category']
# TODO реализовать фильтры поиска по колонкам, рецепт тут: https://medium.com/@hakibenita/how-to-add-a-text-filter-to-django-admin-5d1db93772d8
# TODO экспорт в формат xls https://xlsxwriter.readthedocs.io/index.html


admin.site.register(Category, CategoryAdmin)
admin.site.register(AttributeValue, AttrValAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Manufacturer, BaseAdmin)
admin.site.register(Attribute, AttrAdmin)
admin.site.register(Specification, BaseAdmin)
admin.site.register(DataFile, FileUploadAdmin)

# Register your models here.
