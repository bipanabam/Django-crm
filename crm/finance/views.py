from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from company.decorators import access_level_required

from .services import send_invoice_bill_to_client

from sales.services import get_all_clients, get_all_vouchers
from company.services import get_employees, get_user_branch

from sales.models import Voucher

from .forms import JournalEntryForm, VoucherForm


# Create your views here.
@login_required
@access_level_required(['Admin', 'Manager', 'Accountant'])
def account_overview(request):
    clients = get_all_clients(request)
    vouchers = get_all_vouchers(request)

    context = {
        'clients': clients, 
        'vouchers': vouchers,
    }

    return render(request, 'finance/overview.html', context=context)

def get_accounts_by_type(request):
    account_type = request.GET.get('account_type')
    print(account_type)
    data = []

    if account_type == 'client':
        accounts = get_all_clients(request)
    elif account_type == 'employee':
        accounts = get_employees(request)
    else:
        accounts = []

    data = [{'id': a.id, 'name': a.name} for a in accounts]
    print(data)
    return JsonResponse({'accounts': data})

@login_required
@access_level_required(['Admin', 'Manager', 'Accountant'])
def create_voucher(request):
    if request.method == 'POST':
        form = VoucherForm(request.POST, request=request)
        if form.is_valid():
            with transaction.atomic():
                voucher = form.save(commit=False)
                
                # Assign generic foreign key
                account_type = form.cleaned_data['account_type']
                account_instance = form.cleaned_data['accounts']

                voucher.account_type = account_type  # ContentType object
                voucher.account_id = account_instance.id
                voucher.branch = get_user_branch(request)
                voucher.created_by = request.user
                voucher.save()
            messages.success(request, 'Voucher created successfully')
            return redirect('account_overview')
        else:
            print(form.errors)
    else:
        form = VoucherForm(request=request)
    context = {
        'form': form
    }
    return render(request, 'finance/create_voucher.html', context=context)

@login_required
@access_level_required(['Admin', 'Manager', 'Accountant'])
def edit_voucher(request, voucher_id):
    branch = get_user_branch(request)
    instance = get_object_or_404(Voucher, id=voucher_id, branch=branch)
    if request.method == 'POST':
        form = VoucherForm(request.POST, request=request, instance=instance)
        if form.is_valid():
            with transaction.atomic():
                voucher = form.save(commit=False)
                
                voucher.account_type = form.cleaned_data['account_type']
                voucher.account_id = form.cleaned_data['accounts'].id if form.cleaned_data['accounts'] else None
                voucher.save()
            messages.success(request, 'Voucher updated successfully')
            return redirect('account_overview')
        else:
            print(form.errors)
    else:
        form = VoucherForm(request=request, instance=instance)
    context = {
        'form': form
    }
    return render(request, 'finance/edit_voucher.html', context=context)

@login_required
@access_level_required(['Admin', 'Manager', 'Accountant'])
def delete_voucher(request, voucher_id):
    branch = get_user_branch(request)
    voucher = get_object_or_404(Voucher, id=voucher_id, branch=branch)
    
    if request.method == 'POST':
        voucher.delete()
        messages.success(request, "Voucher deleted successfully.")
        return redirect('sales') 
    return redirect('sales')

@login_required
@access_level_required(['Admin', 'Manager', 'Accountant'])
def invoice_bill_view(request, voucher_id):
    branch = get_user_branch(request)
    invoice = Voucher.objects.get(id=voucher_id, branch=branch)
    context = {
        'invoice': invoice
    }
    return render(request, 'sales/bill/invoice_bill.html', context=context)

@login_required
@access_level_required(['Admin', 'Manager', 'Accountant'])
def approve_voucher(request, voucher_id):
    branch = get_user_branch(request)
    voucher = get_object_or_404(Voucher, id=voucher_id, branch=branch)

    if voucher.account_type.name == "client":
        with transaction.atomic():
            #update client 
            client = voucher.account
            client.advance_paid += voucher.amount
            client.due_amount -= voucher.amount
            if client.due_amount == 0:
                client.status = "Paid"
            client.save()
            voucher.status = "Paid"
            voucher.save()

            # Send the invoice bill after transaction
            try:
                send_invoice_bill_to_client(client.id, invoice=voucher)
            except Exception as email_error:
                print(f"Error sending invoice: {email_error}")
                messages.error(request, "Voucher marked as paid, but email could not be sent.")
            messages.success(request, 'Voucher marked as paid successfully')
        return redirect('account_overview')
    else:
        voucher.status = "Paid"
        voucher.save()
        messages.success(request, 'Voucher marked as paid successfully')
        return redirect('account_overview')