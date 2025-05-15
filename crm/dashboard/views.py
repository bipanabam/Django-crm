from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.db.models import Sum
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm

from datetime import datetime, timedelta

from company.services import get_users
from sales.services import get_all_clients, get_client_with_remaining_dues, get_all_vouchers, get_all_client_vouchers, get_assigned_clients, get_assigned_client_vouchers
from documentation.services import get_all_client_documents, get_all_countries

# Create your views here.
@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    if user.is_superuser:
        return render(request, 'base/dashboard.html')
    if user.role == "admin":
        return render(request, 'dashboard/admin_dashboard.html',  context=get_dashboard_context(request))
    elif user.role == "manager":
        users = get_users(request)
        clients = get_all_clients(request)
        total_clients = clients.count()
        new_clients = new_clients = clients.filter(status__in=["Pending", "In Progress"]).count()

        vouchers = get_all_vouchers(request)
        total_revenue = vouchers.filter(type='Receipt').aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = vouchers.filter(type='Payment').aggregate(total=Sum('amount'))['total'] or 0
        total_profit = total_revenue - total_expenses
        context = {
            'total_clients': total_clients,
            'new_clients': new_clients,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'total_profit': total_profit,
            'clients': clients,
            'vouchers': vouchers,
            'users': users
        }
        return render(request, 'dashboard/manager_dashboard.html', context=context)
    elif user.role == "team manager":
        users = get_users(request)
        total_team_members = users.count()
        total_account_manager = users.filter(role="accountant").count()
        total_sales_manager = users.filter(role="sales representative").count()
        total_marketing_manager = users.filter(role="marketing").count()
        total_document_manager = users.filter(role="counsellor").count()
        context = {
            'users': users, 
            'total_team_members': total_team_members,
            'total_account_manager': total_account_manager,
            'total_sales_manager': total_sales_manager,
            'total_marketing_manager': total_marketing_manager,
            'total_document_manager': total_document_manager
        }
        return render(request, 'dashboard/team_manager_dashboard.html', context=context)
    elif user.role == "accountant":
        clients = get_all_clients(request)
        vouchers = get_all_vouchers(request)
        total_dues = clients.filter(due_amount__gt=0).aggregate(total=Sum('due_amount'))['total'] or 0
        
        total_revenue = vouchers.filter(type='Receipt').aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = vouchers.filter(type='Payment').aggregate(total=Sum('amount'))['total'] or 0
        total_profit = total_revenue - total_expenses

        context = {
            'clients': clients,
            'vouchers': vouchers,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'total_dues': total_dues,
            'total_profit': total_profit
        }
        return render(request, 'dashboard/accountant_dashboard.html', context=context)
    elif user.role == "counsellor":
        clients = get_all_clients(request)
        total_clients = clients.count()

        documents = get_all_client_documents(request)
        total_document_uploaded = documents.count()

        countries_recorded = get_all_countries(request)
        total_countries_recorded = countries_recorded.count()

        context = {
            'total_clients': total_clients, 
            'total_document_uploaded': total_document_uploaded,
            'total_countries_recorded': total_countries_recorded,
            'documents': documents,
        }
        return render(request, 'dashboard/counsellor_dashboard.html', context=context)
    elif user.role == "sales representative":
        clients = get_assigned_clients(request)
        all_clients = get_all_clients(request)
        total_clients = all_clients.count()

        vouchers = get_assigned_client_vouchers(request)
        total_revenue = vouchers.filter(type='Receipt').aggregate(total=Sum('amount'))['total'] or 0

        context = {
            'clients': clients,
            'total_clients': total_clients,
            'total_revenue': total_revenue
        }
        return render(request, 'dashboard/sales_representative_dashboard.html', context=context)
    else:
        return render(request, 'dashboard/marketing_dashboard.html')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = UserLoginForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Perform authentication here
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in successfully.")
                return redirect('dashboard')
            else:
                form.add_error(None, 'Invalid email or password')
                return render(request, 'auth/login.html', {'form': form})
    return render(request, 'auth/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

def sales_chart_data(request):
    days = int(request.GET.get('days', 7))
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days - 1)
    branch_id = request.GET.get('branch_id')

    sales = get_all_vouchers(request).filter(
        category='Sales',
        created_at__date__range=[start_date, end_date]
    )

    if branch_id and branch_id != 'all':
        sales = sales.filter(branch_id=branch_id)
    
    total_income = sales.filter(type='Receipt').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = sales.filter(type='Payment').aggregate(total=Sum('amount'))['total'] or 0

    return JsonResponse({
        "labels": ["Total Income", "Total Expenses"],
        "values": [total_income, total_expense],
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
    })

def revenue_chart_data(request):
    days = int(request.GET.get('days', 7))
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days - 1)
    branch_id = request.GET.get('branch_id')

    revenues = get_all_vouchers(request).filter(
        created_at__date__range=[start_date, end_date]
    )
    
    if branch_id and branch_id != 'all':
        revenues = revenues.filter(branch_id=branch_id)

    total_income = revenues.filter(type='Receipt').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = revenues.filter(type='Payment').aggregate(total=Sum('amount'))['total'] or 0

    return JsonResponse({
        "labels": ["Total Income", "Total Expenses"],
        "values": [total_income, total_expense],
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
    })


def admin_dashboard_partial(request):
    # HTMX partial load
    branch_id = request.POST.get('branch_id')
    request.session['branch_id'] = branch_id
    context = get_dashboard_context(request)
    html = render_to_string('dashboard/_partials/_dashboard_content.html', context, request=request)
    return HttpResponse(html)

def get_dashboard_context(request):
    branch_id = request.session.get('branch_id')

    if not branch_id or branch_id == 'all':
        users = get_users(request)
        clients = get_all_clients(request)
        vouchers = get_all_vouchers(request)
    else:
        users = get_users(request).filter(profile__branch_id=branch_id)
        clients = get_all_clients(request).filter(branch_id=branch_id)
        vouchers = get_all_vouchers(request).filter(branch_id=branch_id)

    total_clients = clients.count()
    new_clients = clients.filter(status__in=["Pending", "In Progress"]).count()
    total_revenue = vouchers.filter(type='Receipt').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = vouchers.filter(type='Payment').aggregate(total=Sum('amount'))['total'] or 0
    total_profit = total_revenue - total_expenses

    new_sales = vouchers.filter(category='Sales', created_at__gte=datetime.now()-timedelta(days=7)).count()

    return {
        'total_clients': total_clients,
        'new_clients': new_clients,
        'new_sales': new_sales,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'total_profit': total_profit,
        'clients': clients,
        'vouchers': vouchers,
        'users': users,
    }
