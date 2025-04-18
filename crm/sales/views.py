from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from django.forms import inlineformset_factory

from .models import ClientDocument, Client

from .forms import ClientForm, ClientDocumentForm,ClientDocumentFormset

from . import services
from company.services import get_user_branch

# Create your views here.
def sales_view(request):
    clients = services.get_all_clients(request)

    context = {
        'clients': clients
    }

    return render(request, 'sales/overview.html', context=context)

def inquiry_form_view(request):
    document_types = [
        'Passport Size Photograph',
        'Passport Image',
        'Citizenship Image (Front)',
        'Citizenship Image (Back)',
    ]
    client_form = ClientForm()
    
    # Create formset with initial document_type values
    document_formset = ClientDocumentFormset(
        queryset=ClientDocument.objects.none(),
        initial=[{'document_type': dt} for dt in document_types]
    )

    context = {
        'form': client_form,
        'document_formset': document_formset,
    }

    if request.method == 'POST':
        client_form = ClientForm(request.POST)
        document_formset = ClientDocumentFormset(request.POST, request.FILES)
        if client_form.is_valid() and document_formset.is_valid():
            with transaction.atomic():
                client = client_form.save(commit=False)
                client.branch = get_user_branch(request)
                client.created_by = request.user
                client.save()
                for form in document_formset:
                    document = form.save(commit=False)
                    document.client = client
                    document.save()
                return redirect('sales')
        else:
            context['form'] = client_form
            context['document_formset'] = document_formset
            return render(request, 'sales/inquiry_form.html', context=context)

    return render(request, 'sales/inquiry_form.html', context=context)
def edit_client(request, client_id):
    client = services.get_client(request, client_id)
    client_form = ClientForm(instance=client)
    formset_class = inlineformset_factory(
        Client, ClientDocument, form=ClientDocumentForm,
        extra=0, can_delete=True,
    )
    document_formset = formset_class(instance=client)

    if request.method == 'POST':
        client_form = ClientForm(request.POST, instance=client)
        document_formset = formset_class(request.POST, request.FILES, instance=client)
        if client_form.is_valid() and document_formset.is_valid():
            client_form.save()
            document_formset.save()
            messages.success(request, 'Client details updated successfully')
            return redirect('sales')
        else:
            print(client_form.errors)
            print(document_formset.errors)
    context = {
        'form': client_form,
        'document_formset': document_formset,
        'client': client,
    }
    return render(request, 'sales/edit_client.html', context=context)