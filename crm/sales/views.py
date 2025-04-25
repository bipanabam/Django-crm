from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory

from django.utils import timezone

from .models import ClientDocument, Client, Voucher

from .forms import ClientForm, ClientDocumentForm,ClientDocumentFormset, AssignClientForm, InvoiceForm

from . import services
from company.services import get_user_branch

# Create your views here.
@login_required
def sales_view(request):
    clients = services.get_all_clients(request)
    branch = get_user_branch(request)
    sales = clients.filter(status="Pending")

    vouchers = services.get_all_client_vouchers(request)

    assign_client_form = AssignClientForm(branch=branch)
    if request.method == 'POST':
        assign_client_form = AssignClientForm(request.POST, branch=branch)
        if assign_client_form.is_valid():
            client = assign_client_form.cleaned_data['client']
            sales_representative = assign_client_form.cleaned_data['sales_representative']
            client.assigned_to = sales_representative
            client.assigned_date = timezone.now()
            client.save()
            messages.success(request, f'Client {client.name} assigned to {sales_representative.first_name} {sales_representative.last_name} successfully')
            return redirect('sales')
        else:
            print(assign_client_form.errors)

    context = {
        'clients': clients, 
        'assign_client_form': assign_client_form,
        'sales': sales,
        'vouchers': vouchers,
    }

    return render(request, 'sales/overview.html', context=context)

@login_required
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
                if client.advance_paid > 0:
                    client.status = "Pending"
                    # Create Voucher
                    Voucher.objects.create(
                        branch = client.branch,
                        client=client,
                        type = "Receipt",
                        category = "Sales",
                        amount = client.advance_paid,
                        narration = "Advance paid while inquiry.",
                        created_by = request.user,
                        status = "Paid",
                    )
                    
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

@login_required
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

def get_due_amount(request):
    client_id = request.GET.get('client_id')
    branch = services.get_user_branch(request)
    try:
        client = Client.objects.get(id=client_id, branch=branch)
        return JsonResponse({'due_amount': client.due_amount})
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Client not found'}, status=404)

@login_required
def create_invoice(request):
    branch = services.get_user_branch(request)
    form = InvoiceForm(request=request)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request=request)
        if form.is_valid():
            with transaction.atomic():
                voucher = form.save(commit=False)
                voucher.branch = branch
                voucher.type = "Receipt"
                voucher.category = "Sales"
                voucher.created_by = request.user
                voucher.save()
            messages.success(request, 'Invoice created successfully')
            return redirect('sales')
        else:
            print(form.errors)
    context = {
        'form': form
    }
    return render(request, 'sales/create_invoice.html', context=context)


@login_required
def edit_invoice(request, voucher_id):
    branch = services.get_user_branch(request)
    instance = get_object_or_404(Voucher, id=voucher_id, branch=branch)
    previous_amount = instance.amount
    
    form = InvoiceForm(request=request, instance=instance)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request=request, instance=instance)
        if form.is_valid():
            with transaction.atomic():
                voucher = form.save(commit=False)
                updated_amount = voucher.amount
                if updated_amount != previous_amount:
                    #update client 
                    client = voucher.client
                    client.due_amount = (client.due_amount + previous_amount ) - updated_amount
                    client.advance_paid = (client.advance_paid - previous_amount ) + updated_amount
                    if client.due_amount == 0:
                        client.status = "Paid"
                    client.save()
                voucher.save()
            messages.success(request, 'Invoice updated successfully')
            return redirect('sales')
    context = {
        'form': form
    }
    return render(request, 'sales/edit_invoice.html', context=context)

@login_required
def delete_invoice(request, voucher_id):
    branch = get_user_branch(request)
    voucher = get_object_or_404(Voucher, id=voucher_id, branch=branch)
    
    if request.method == 'POST':
        # update client
        print(voucher)
        if voucher.account_type == "client":
            client = voucher.account
            print(client)
            client.advance_paid -= voucher.amount
            client.due_amount += voucher.amount
            if client.due_amount > 0:
                client.status = "Pending"
            client.save()
        
        voucher.delete()
        messages.success(request, "Invoice deleted successfully.")
        return redirect('sales') 
    return redirect('sales')