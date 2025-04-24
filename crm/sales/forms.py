from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import modelformset_factory

from .models import Client, ClientDocument, Voucher

from . import services

from company.models import User

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

class AssignClientForm(forms.Form):
    client = forms.ModelChoiceField(
        queryset=Client.objects.none(), 
        label='Select Client',
        empty_label='Select Client'
        )
    sales_representative = forms.ModelChoiceField(
        queryset=Client.objects.none(), 
        label='Assigned to:',
        empty_label='Select Sales Representative')

    def __init__(self, *args, **kwargs):
        branch = kwargs.pop('branch', None)
        super(AssignClientForm, self).__init__(*args, **kwargs)

        if branch is not None:
            self.fields['client'].queryset = services.get_unassigned_clients(branch=branch)
            self.fields['sales_representative'].queryset = User.objects.filter(profile__branch=branch, role='sales representative').distinct()

class InvoiceForm(forms.ModelForm):
    client = forms.ModelChoiceField(queryset=Client.objects.none())

    class Meta:
        model = Voucher
        fields = ['client', 'amount', 'payment_method', 'narration']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(InvoiceForm, self).__init__(*args, **kwargs)

        if request:
            self.fields['client'].queryset = services.get_client_with_remaining_dues(request)

        # Set initial value for client field if editing
        if self.instance.pk and self.instance.account_type and self.instance.account_id:
            if self.instance.account_type.model_class() == Client:
                try:
                    self.fields['client'].initial = self.instance.account_type.get_object_for_this_type(id=self.instance.account_id)
                    self.fields['client'].disabled = True
                except Client.DoesNotExist:
                    pass

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get('client')
        amount = cleaned_data.get('amount')

        if client and amount is not None:
            due_amount = client.due_amount

            if self.instance.pk:  # While editing an existing voucher
                old_amount = self.instance.amount if self.instance.amount else 0
                allowed_amount = due_amount + old_amount
            else:
                allowed_amount = due_amount

            if amount > allowed_amount:
                self.add_error(
                    'amount',
                    f"The entered amount exceeds the allowed amount of {allowed_amount:.2f}."
                )

    def save(self, commit=True):
        instance = super().save(commit=False)

        if not instance.pk: 
            client = self.cleaned_data['client']
            instance.account_type = ContentType.objects.get_for_model(Client)
            instance.account_id = client.id

        if commit:
            instance.save()
        return instance


