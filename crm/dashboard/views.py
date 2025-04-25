from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Sum

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm

from datetime import datetime, timedelta

from company.services import get_users
from sales.services import get_all_clients, get_all_vouchers, get_all_client_vouchers

# Create your views here.
@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    if user.is_superuser:
        return render(request, 'base/dashboard.html')
    if user.role == "admin":
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
            'vouchers': vouchers
        }
        return render(request, 'dashboard/admin_dashboard.html', context=context)
    elif user.role == "manager":
        return render(request, 'dashboard/manager_dashboard.html')
    elif user.role == "team manager":
        users = get_users(request)
        context = {
            'users': users
        }
        return render(request, 'dashboard/team_manager_dashboard.html', context=context)
    elif user.role == "accountant":
        return render(request, 'dashboard/accountant_dashboard.html')
    elif user.role == "counsellor":
        return render(request, 'dashboard/counsellor_dashboard.html')
    elif user.role == "sales representative":
        return render(request, 'dashboard/sales_representative_dashboard.html')
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

    sales = get_all_vouchers(request).filter(
        category='Sales',
        created_at__date__range=[start_date, end_date]
    )
    
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

    revenues = get_all_vouchers(request).filter(
        created_at__date__range=[start_date, end_date]
    )
    
    total_income = revenues.filter(type='Receipt').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = revenues.filter(type='Payment').aggregate(total=Sum('amount'))['total'] or 0

    return JsonResponse({
        "labels": ["Total Income", "Total Expenses"],
        "values": [total_income, total_expense],
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
    })

