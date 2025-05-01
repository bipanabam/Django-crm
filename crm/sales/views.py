from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.db import transaction
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory

from django.utils import timezone

from company.decorators import access_level_required

from .models import ClientDocument, Client, Voucher

from .forms import ClientForm, ClientDocumentForm,ClientDocumentFormset, AssignClientForm, InvoiceForm

from . import services
from company.services import get_user_branch

# Create your views here.
@login_required
def revenue_chart_data_by_year(request):
    current_year = timezone.now().year
    previous_year = current_year - 1
    all_vouchers = services.get_all_vouchers(request)

    def get_monthly_revenue(year, all_vouchers):
        monthly_totals = [0] * 12
        vouchers = (
            all_vouchers.filter(type='Receipt', created_at__date__year=year)
            .annotate(month=TruncMonth('created_at__date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        for entry in vouchers:
            month_index = entry['month'].month - 1
            monthly_totals[month_index] = float(entry['total'])
        return monthly_totals

    this_year_data = get_monthly_revenue(current_year, all_vouchers)
    last_year_data = get_monthly_revenue(previous_year, all_vouchers)

    return JsonResponse({
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "current_year": current_year,
        "previous_year": previous_year,
        "this_year_revenue": this_year_data,
        "last_year_revenue": last_year_data
    })

@login_required
@access_level_required(['Admin', 'Manager', 'Counsellor', 'Sales Representative'])
def sales_view(request):
    branch = get_user_branch(request)

    if request.user.role == 'sales representative':
        clients = services.get_assigned_clients(request)
    else:
        clients = services.get_all_clients(request)
    sales = clients.filter(status="Pending")

    if request.user.role == 'sales representative':
        vouchers = services.get_assigned_client_vouchers(request)
    else:
        vouchers = services.get_all_client_vouchers(request)

    # revenue
    all_vouchers = services.get_all_vouchers(request)
    total_revenue = vouchers.filter(type='Receipt').aggregate(total=Sum('amount'))['total'] or 0

    assign_client_form = AssignClientForm(branch=branch)
    if request.method == 'POST':
        if request.user.role == 'admin' or request.user.role == 'manager':
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
        else:
            messages.error(request, "You don't have permission to assign clients")

    context = {
        'clients': clients, 
        'assign_client_form': assign_client_form,
        'sales': sales,
        'vouchers': vouchers,
        'total_revenue': total_revenue
    }

    return render(request, 'sales/overview.html', context=context)

@login_required
@access_level_required(['Admin', 'Manager', 'Counsellor'])
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
                    paid_amount = client.advance_paid
                    client.advance_paid = 0
                    client.due_amount = client.package_amount
                    client.status = "Pending"
                    client.created_by = request.user
                    client.save()
                    # Create Voucher
                    account_type = ContentType.objects.get_for_model(Client)
                    account_id = client.id
                    Voucher.objects.create(
                        branch = client.branch,
                        account_type=account_type,
                        account_id=account_id,
                        type = "Receipt",
                        category = "Sales",
                        amount = paid_amount,
                        narration = "Advance paid while inquiry.",
                        created_by = request.user,
                        status = "Pending",
                    )
                else:
                    client.created_by = request.user
                    client.save()
                for form in document_formset:
                    document = form.save(commit=False)
                    document.client = client
                    document.save()
                messages.success(request, 'Client created successfully')
                return redirect('sales')
        else:
            context['form'] = client_form
            context['document_formset'] = document_formset
            return render(request, 'sales/inquiry_form.html', context=context)

    return render(request, 'sales/inquiry_form.html', context=context)

@login_required
@access_level_required(['Admin', 'Manager', 'Counsellor'])
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

@login_required
@access_level_required(['Admin', 'Manager', 'Counsellor'])
def delete_client(request, client_id):
    branch = get_user_branch(request)
    client = get_object_or_404(Client, id=client_id, branch=branch)
    
    if request.method == 'POST':
        client.delete()
        messages.success(request, "Client deleted successfully.")
        return redirect('sales') 
    return redirect('sales')

def get_due_amount(request):
    client_id = request.GET.get('client_id')
    branch = services.get_user_branch(request)
    try:
        client = Client.objects.get(id=client_id, branch=branch)
        return JsonResponse({'due_amount': client.due_amount})
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Client not found'}, status=404)

@login_required
@access_level_required(['Admin', 'Manager', 'Counsellor', 'Sales Representative'])
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
@access_level_required(['Admin', 'Manager', 'Counsellor', 'Sales Representative'])
def edit_invoice(request, voucher_id):
    branch = services.get_user_branch(request)
    instance = get_object_or_404(Voucher, id=voucher_id, branch=branch)
    
    form = InvoiceForm(request=request, instance=instance)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request=request, instance=instance)
        if form.is_valid():
            with transaction.atomic():
                voucher = form.save(commit=False)
                voucher.save()
            messages.success(request, 'Invoice updated successfully')
            return redirect('sales')
    context = {
        'form': form
    }
    return render(request, 'sales/edit_invoice.html', context=context)

@login_required
@access_level_required(['Admin', 'Manager', 'Counsellor', 'Sales Representative'])
def delete_invoice(request, voucher_id):
    branch = get_user_branch(request)
    voucher = get_object_or_404(Voucher, id=voucher_id, branch=branch)
    
    if request.method == 'POST':
        # update client
        if voucher.account_type == "client":
            client = voucher.account
            client.due_amount += voucher.amount
            if client.due_amount > 0:
                client.status = "Pending"
            client.save()
        
        voucher.delete()
        messages.success(request, "Invoice deleted successfully.")
        return redirect('sales') 
    return redirect('sales')