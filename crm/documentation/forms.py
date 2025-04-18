from django import forms
from django.forms import inlineformset_factory, modelformset_factory, BaseModelFormSet
from django.core.exceptions import ValidationError

from .models import Country, DocumentType, CountryWiseClientDocument

from sales.models import Client

from sales.services import get_all_clients
from .services import get_all_countries

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name']
        labels = {
            'name': 'Country Name'
        }

    def __init__(self, *args, **kwargs):
        super(CountryForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Enter your Country Name'

class DocumentTypeForm(forms.ModelForm):
    class Meta:
        model = DocumentType
        fields = ['document_title']

    def __init__(self, *args, **kwargs):
        super(DocumentTypeForm, self).__init__(*args, **kwargs)
        self.fields['document_title'].widget.attrs['placeholder'] = 'Add document title'

DocumentFormSet = inlineformset_factory(
    Country, DocumentType, form=DocumentTypeForm,
    extra=1, can_delete=True
)

class CountryWiseClientDocumentForm(forms.ModelForm):
    class Meta:
        model = CountryWiseClientDocument
        fields = ['country', 'client', 'document_type', 'document_file']
        labels = {
            'country': 'Select Country',
            'client': 'Enter Client Name',
            'document_type': 'Select Document Type',
            'document_file': 'Choose Document file'
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(CountryWiseClientDocumentForm, self).__init__(*args, **kwargs)
        self.fields['country'].queryset = get_all_countries(request)
        self.fields['client'].queryset = get_all_clients(request)
        self.fields['document_type'].queryset = DocumentType.objects.none()

        # Check if this form is being submitted
        if self.is_bound:
            country_field_name = self.add_prefix('country')
            document_type_field_name = self.add_prefix('document_type')
            country_id = self.data.get(country_field_name)
            if country_id:
                try:
                    country_id = int(country_id)
                    self.fields['document_type'].queryset = DocumentType.objects.filter(country_id=country_id)
                except (ValueError, TypeError):
                    pass
        elif self.instance.pk:
            self.fields['document_type'].queryset = DocumentType.objects.filter(country=self.instance.country)

class BaseCountryWiseClientDocumentFormSet(BaseModelFormSet):
    def clean(self):
        super(BaseCountryWiseClientDocumentFormSet, self).clean()
        seen = set()
        for form in self.forms:
            if form.cleaned_data.get('DELETE'):
                continue  # Skip deleted forms

            country = form.cleaned_data.get('country')
            client = form.cleaned_data.get('client')
            document_type = form.cleaned_data.get('document_type')

            if country and client and document_type:
                key = (country.id, client.id, document_type.id)
                if key in seen:
                    raise ValidationError("Each document type must be unique per country and client.")
                seen.add(key)

CountryWiseClientDocumentFormSet = modelformset_factory(
    CountryWiseClientDocument,
    form=CountryWiseClientDocumentForm,
    formset=BaseCountryWiseClientDocumentFormSet,
    extra=1,  # number of empty forms shown by default
    can_delete=True  # allows deletion of entries
)