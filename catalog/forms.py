from django import forms
from .choices import TYPES_SEARCH
from .models import AttributeValue, Manufacturer


class ProductChangeListForm(forms.ModelForm):
    # here we only need to define the field we want to be editable
    attrs_vals = forms.ModelMultipleChoiceField(
        queryset=AttributeValue.objects.only('title').all(), required=False)
   

class SearchFromFile(forms.Form):
    file = forms.FileField(label='Файл')
    manufacturer_from = forms.ModelChoiceField(label='Исходный производитель', empty_label=None, queryset=Manufacturer.objects.all())
    manufacturer_to = forms.ModelChoiceField(label='Необходимый производитель', empty_label=None, queryset=Manufacturer.objects.all())


class SearchForm(forms.Form):
    article = forms.CharField(label='Артикул')
    #cc = forms.ComboField(fields=[forms.CharField(max_length=20), forms.EmailField()])
    manufacturer_from = forms.ModelChoiceField(label='Исходный производитель', empty_label=None, queryset=Manufacturer.objects.all())
    manufacturer_to = forms.ModelChoiceField(label='Необходимый производитель', empty_label=None, queryset=Manufacturer.objects.all())
    advanced_search = forms.BooleanField(label='Расширенный поиск', widget=forms.CheckboxInput, required=False)
    

class AdvancedSearchForm(forms.Form):
    article = forms.CharField(label='Артикул', widget=forms.TextInput(attrs={'readonly':'readonly'}))#, disabled=True, required=False)
    # advanced_search = forms.BooleanField(label='Расширенный поиск', widget=forms.CheckboxInput, required=False)
    #forms.CharField()
    # hrd_attrs = forms.ChoiceField(label='hrd attr', choices=('ss', 'gg'), required=False)

    def __init__(self, *args, **kwargs):
        extra_fields = kwargs.pop('extra', 0)
    
        # check if extra_fields exist. If they don't exist assign 0 to them
        # if not extra_fields:
        #     extra_fields = 0
    
        super(AdvancedSearchForm, self).__init__(*args, **kwargs)
        #self.fields['total_input_fields'].initial = extra_fields
    
        for index in extra_fields:
            # generate extra fields in the number specified via extra_fields
            self.fields['extra_field_{index}'.format(index=index[2])] = forms.ChoiceField(label=index[0],
                                                                                          required=False,
                                                                                          choices=TYPES_SEARCH)