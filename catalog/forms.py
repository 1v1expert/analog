from django import forms
from .models import AttributeValue


class ProductChangeListForm(forms.ModelForm):
    # here we only need to define the field we want to be editable
    attrs_vals = forms.ModelMultipleChoiceField(
        queryset=AttributeValue.objects.only('title').all(), required=False)
    
class SearchForm(forms.ModelForm):
    article = forms.CharField()
    