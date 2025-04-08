from django.shortcuts import render, redirect
from django.db import transaction

from .models import ClientDocument

from .forms import ClientForm, ClientDocumentFormset

from . import services
from company.services import get_user_branch

# Create your views here.
def sales_view(request):
    if request.user.role == 'admin':
        clients = services.get_all_clients(request)
    else:
        clients = services.get_branch_clients(request)

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
                print(client)
                for form in document_formset:
                    document = form.save(commit=False)
                    document.client = client
                    document.save()
                    print(document)
                return redirect('sales')
        else:
            context['form'] = client_form
            context['document_formset'] = document_formset
            return render(request, 'sales/inquiry_form.html', context=context)

    return render(request, 'sales/inquiry_form.html', context=context)
