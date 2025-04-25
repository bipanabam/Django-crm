from django import forms
from django.forms import inlineformset_factory
from django.contrib.contenttypes.models import ContentType

from .models import JournalEntry

from sales.models import Voucher, Client

from company.services import get_employees
from sales.services import get_all_clients


class VoucherForm(forms.ModelForm):
    account_type = forms.ChoiceField(choices=[
        ('', 'Select Account Type'),
        ('client', 'Client'),
        ('employee', 'Employee'),
        # Add more here
    ])
    accounts = forms.ModelChoiceField(queryset=Client.objects.none(), required=False)


    class Meta:
        model = Voucher
        fields = ['type', 'category', 'account_type', 'accounts', 'amount', 'payment_method', 'narration',]

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['accounts'].queryset = Client.objects.none()

        if self.instance and self.instance.pk:
            model_name = self.instance.account_type.model if self.instance.account_type else None
            self.initial['account_type'] = model_name

            # Set appropriate queryset for 'accounts' field based on model
            if model_name == 'client':
                self.fields['accounts'].queryset = get_all_clients(request)
                self.initial['accounts'] = self.instance.account
            elif model_name == 'employee':
                self.fields['accounts'].queryset = get_employees(request)
                self.initial['accounts'] = self.instance.account
        else:
            account_type = self.data.get('account_type')
            if account_type == 'client':
                self.fields['accounts'].queryset = get_all_clients(request)
            elif account_type == 'employee':
                self.fields['accounts'].queryset = get_employees(request)

    def clean(self):
        cleaned_data = super().clean()
        account_type = cleaned_data.get('account_type')

        # Check for account_type and convert it to ContentType instance
        if account_type:
            try:
                content_type = ContentType.objects.get(model=account_type)
                cleaned_data['account_type'] = content_type
            except ContentType.DoesNotExist:
                raise forms.ValidationError("Invalid account type selected.")
        return cleaned_data

class JournalEntryForm(forms.ModelForm):
    account_type = forms.ChoiceField(choices=[
        ('client', 'Client'),
        ('employee', 'Employee'),
    ])
    account = forms.ChoiceField(choices=[])

    class Meta:
        model = JournalEntry
        fields = ['account_type', 'debit', 'credit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].choices = [('', '--- Select ---')]

    def clean(self):
        cleaned_data = super().clean()
        debit = cleaned_data.get('debit', 0)
        credit = cleaned_data.get('credit', 0)

        if debit < 0 or credit < 0:
            raise forms.ValidationError("Debit and Credit cannot be negative.")

        # Custom validation to ensure the journal entries balance out
        if debit and credit:
            if debit != credit:
                raise forms.ValidationError("Debit and Credit amounts must balance.")
        return cleaned_data

JournalEntryFormSet = inlineformset_factory(
    Voucher,
    JournalEntry,
    form=JournalEntryForm,
    extra=2,  # number of empty entries
    can_delete=True
)