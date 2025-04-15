from django import forms
from django.forms import modelformset_factory

from .models import Client, ClientDocument

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'address', 'contact_number', 'email_address', 'nationality', 'father_name', 'mother_name', 'preferred_country', 'visa_type', 'package_amount', 'advance_paid', 'due_amount', 'more_remarks']


class ClientDocumentForm(forms.ModelForm):
    class Meta:
        model = ClientDocument
        fields = ['document']
        # labels = {
        #     'document_type': 'Document Type',
        #     'document': 'Attach Document',
        # }
        widgets = {
            'document_type': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(ClientDocumentForm, self).__init__(*args, **kwargs)
        self.fields['document'].widget.attrs['placeholder'] = 'Upload'

ClientDocumentFormset = modelformset_factory(
    ClientDocument, ClientDocumentForm,
    fields=('document_type', 'document'), extra=4)