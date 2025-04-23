from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm

from company.services import get_users

# Create your views here.
@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    if user.is_superuser:
        return render(request, 'base/dashboard.html')
    if user.role == "admin":
        return render(request, 'dashboard/admin_dashboard.html')
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