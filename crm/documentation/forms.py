from django import forms
from django.forms import inlineformset_factory, modelformset_factory

from .models import Country, DocumentType, CountryWiseClientDocument

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name']

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

    def __init__(self, *args, **kwargs):
        super(CountryWiseClientDocumentForm, self).__init__(*args, **kwargs)


CountryWiseClientDocumentFormSet = modelformset_factory(
    CountryWiseClientDocument,
    form=CountryWiseClientDocumentForm,
    extra=1,  # number of empty forms shown by default
    can_delete=True  # allows deletion of entries
)