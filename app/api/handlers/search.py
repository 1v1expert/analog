from django.http import JsonResponse
from django.views import View

from catalog.models import Product, Manufacturer
from catalog.forms import AdvancedSearchForm, SearchForm
from catalog.exceptions import AnalogNotFound, ArticleNotFound, InternalError
import traceback


def get_product_info(analog, original=None):
    info = [{"analog":
                 {"name": "наименование", "value": analog.title},
             "original":
                 {"name": "наименование", "value": original.title}
             }]
    
    original_info = original.get_info()
    analog_get_info = analog.get_info()
    
    fixed_attributes = []  # for find images in groups
    
    for attr in analog_get_info:
        analog_name = attr.attribute.title
        orig_attr = None
        
        if analog_name in ('ед.изм', 'цена'):
            continue
        
        for original_attr in original_info:
            print(original_attr.attribute.title, analog_name)
            if original_attr.attribute.title == analog_name:
                orig_attr = original_attr
                break
        
        analog_info = {'name': analog_name}
        
        if attr.attribute.is_fixed:
            analog_value = attr.value.title
            original_value = orig_attr.value.title if orig_attr else ""
            fixed_attributes.append(attr.value)  # for search group with image
        else:
            analog_value = attr.un_value
            original_value = orig_attr.value if orig_attr else ""
        
        analog_info['value'] = analog_value
        
        info.append({"analog": analog_info,
                     "original":
                         {"name": analog_info["name"], "value": original_value}
                     })
    
    info.append({"analog":
                     {"name": "производитель", "value": analog.manufacturer.title},
                 "original":
                     {"name": "производитель", "value": original.manufacturer.title}
                 })
    # find group with image
    if not len(fixed_attributes):
        return {"result": info}
    
    from catalog.models import GroupSubclass
    try:
        group = GroupSubclass.objects.get(category=analog.category,
                                          fixed_attribute__in=fixed_attributes)
        return {"result": info, "image": group.image.url}
    
    except GroupSubclass.DoesNotExist:
        pass
    except GroupSubclass.MultipleObjectsReturned:
        pass
    
    return {"result": info}


def get_analog(article: str = None, manufacturer_to: Manufacturer = None) -> dict:
    product = Product.objects.filter(article=article,
                                     is_enabled=True).first()
    if not product:
        raise ArticleNotFound("Артикул {} не найден".format(article),
                              "Article: {}, manufacturer to: {}".format(article, manufacturer_to))
    
    try:
        analog_pk = product.raw['analogs'][manufacturer_to.title]
        analog = Product.objects.get(pk=analog_pk)
        info = get_product_info(analog=analog, original=product)
        return {"analog": analog, "info": info, "product": product}
    
    except (KeyError, TypeError):
        search = SearchProducts(product=product, manufacturer_to=manufacturer_to)
        search.global_search()
        analog = search.founded_products.first()
        if not analog:
            raise AnalogNotFound('Аналог по артикулу: {} не найден'.format(article),
                                 "Not find analog for article: {}, manufacturer to: {}".format(article,
                                                                                               manufacturer_to))
        info = get_product_info(analog=analog, original=product)
        
        if product.raw is None:
            product.raw = {"analogs": {manufacturer_to.title: analog.pk}}
        else:
            product.raw['analogs'].update({manufacturer_to.title: analog.pk})
        product.save()
        
        return {"analog": analog, "info": info, "product": product}
    
    except Exception as e:
        raise InternalError('Аналог не найден', "Internal error: \n{}".format(traceback.format_exc()))


class SearchView(View):
    LIMIT_VIEW = 50
    
    def get(self, request):
        article = request.GET.get("article")
        
        if article is not None and len(article) > 1:
            return JsonResponse(list(
                Product.objects.filter(
                    article__istartswith=article #, is_enabled=True  # todo: maybe use later
                ).extra(
                    select={'value': 'article'}
                ).values(
                    'value',
                    'title',
                    'manufacturer__title'
                )[:self.LIMIT_VIEW]
            ), safe=False)

        return JsonResponse({'error': "Not found"})
    
    def post(self, request):
        form = SearchForm(request.POST)
        if form.is_valid():
        
            article = form.cleaned_data['article']
            manufacturer_to = form.cleaned_data['manufacturer_to']
        
            try:
                result = get_analog(article=article, manufacturer_to=manufacturer_to)
                return JsonResponse({
                    'result': [result["analog"].article],
                    'info': result["info"].get("result"),
                    "image": result["info"].get("image"),
                    'result_pk': result["analog"].pk,
                    'original_pk': result["product"].pk,
                    'error': False
                })
            except Exception as e:
                return JsonResponse({'result': [], 'error': e.args[0]})
    
        return JsonResponse({'error': 'Некорректно заполненные данные.'})
