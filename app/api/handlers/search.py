from django.http import JsonResponse
from django.views import View

from catalog.models import Product, Manufacturer
from catalog.forms import AdvancedSearchForm, SearchForm
from catalog.utils import AnalogSearch
from catalog.exceptions import AnalogNotFound, ArticleNotFound, InternalError
import traceback


def get_product_info(analog: Product, original: Product):
    info = list()
    info.append(
        {
            "analog":
                {
                    "name": "наименование", "value": analog.title
                },
            "original":
                {
                    "name": "наименование", "value": original.title
                }
        }
    )

    matching = {
        analog.pk: "analog",
        original.pk: "original"
    }
    
    for attribute__pk, group in original.comparison(analog):
        elements = list(group)
        
        element1 = elements[0]
        if len(elements) == 2:
            element2 = elements[1]
            info.append({
                matching[element1["product__pk"]]: {
                    "name": element1["attribute__title"].lower(),
                    "value": element1["value__title"] if element1["value__title"] is not None else element1["un_value"]
                },
                matching[element2["product__pk"]]: {
                    "name": element2["attribute__title"].lower(),
                    "value": element2["value__title"] if element2["value__title"] is not None else element2["un_value"]
                },
            })
            
        elif len(elements) == 1:
            product__pk = [key for key in matching.keys() if key != element1["product__pk"]][0]
            info.append({
                matching[element1["product__pk"]]: {
                    "name": element1["attribute__title"].lower(),
                    "value": element1["value__title"] if element1["value__title"] is not None else element1["un_value"]
                },
                
                matching[product__pk]: {
                    "name": element1["attribute__title"].lower(),
                    "value": "------"
                },
            })

    info.append(
        {
            "analog":
                {
                    "name": "производитель", "value": analog.manufacturer.title
                },
            "original":
                {
                    "name": "производитель", "value": original.manufacturer.title
                }
        }
    )

    return {"result": info}


class SearchProducts(object):
    def __init__(self, product=None, manufacturer_to=None):
        self.product = product
        self.manufacturer_to = manufacturer_to
        self.founded_products = Product.objects.filter(pk=2346)
    def global_search(self):
        pass
    

def get_analog(article: str = None, manufacturer_to: Manufacturer = None) -> dict:
    product = Product.objects.filter(article=article).first()
                                     #is_enabled=True).first()
    if not product:
        raise ArticleNotFound("Артикул {} не найден".format(article),
                              "Article: {}, manufacturer to: {}".format(article, manufacturer_to))
    
    try:
        analog_pk = product.raw['analogs'][manufacturer_to.title]
        analog = Product.objects.get(pk=analog_pk)
        info = get_product_info(analog=analog, original=product)
        return {"analog": analog, "info": info, "product": product}
    
    except (KeyError, TypeError):
        search = AnalogSearch(product_from=product, manufacturer_to=manufacturer_to)
        search.build()
        analog = search.product
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
