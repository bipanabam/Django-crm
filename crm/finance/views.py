from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from sales.services import get_all_clients, get_all_vouchers
from company.services import get_user_branch

from sales.models import Voucher


# Create your views here.
@login_required
def account_overview(request):
    clients = get_all_clients(request)

    vouchers = get_all_vouchers(request)

    context = {
        'clients': clients, 
        'vouchers': vouchers,
    }

    return render(request, 'finance/overview.html', context=context)


@login_required
def approve_voucher(request, voucher_id):
    branch = get_user_branch(request)
    voucher = get_object_or_404(Voucher, id=voucher_id, branch=branch)
    with transaction.atomic():
        #update client 
        client = voucher.client
        client.due_amount -= voucher.amount
        client.advance_paid += voucher.amount
        if client.due_amount == 0:
            client.status = "Paid"
        client.save()
        voucher.status = "Paid"
        voucher.save()
        messages.success(request, 'Voucher marked as paid successfully')
    return redirect('account_overview')