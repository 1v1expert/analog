from django import forms
from .models import AttributeValue, Manufacturer


class ProductChangeListForm(forms.ModelForm):
    # here we only need to define the field we want to be editable
    attrs_vals = forms.ModelMultipleChoiceField(
        queryset=AttributeValue.objects.only('title').all(), required=False)
   
   
class SearchForm(forms.Form):
    article = forms.CharField(label='Артикул')
    #cc = forms.ComboField(fields=[forms.CharField(max_length=20), forms.EmailField()])
    manufacturer_from = forms.ModelChoiceField(label='Исходный производитель', empty_label=None, queryset=Manufacturer.objects.all())
    manufacturer_to = forms.ModelChoiceField(label='Необходимый производитель', empty_label=None, queryset=Manufacturer.objects.all())
    advanced_search = forms.BooleanField(label='Расширенный поиск', widget=forms.CheckboxInput, required=False)
    
class AdvancedeSearchForm(forms.Form):
    article = forms.CharField(label='Артикул')