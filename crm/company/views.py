from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.views.generic import (CreateView, DetailView, UpdateView)

from django.contrib.auth.decorators import login_required
from .decorators import access_level_required

from .models import Branch, User, Employee
from .forms import BranchForm, UserForm, UserUpdateForm, UserSettingForm, EmployeeForm
from . import services

# Create your views here.
@login_required
@access_level_required(['Admin'])
def branch_view(request, *args, **kwargs):
    form = BranchForm(request.POST)
    branches = Branch.objects.all()
    context = {
        'form': form,
        'branches': branches,
    }
    if request.method == 'POST':
        if form.is_valid():
            branch = form.save(commit=False)
            branch.company = request.user.profile.branch.company
            branch.save()
            messages.success(request, 'Branch created successfully.')
            return redirect('branches')
        else:
            messages.error(request, 'Error occurred while adding branch.')
            return render(request, 'branch/branches.html', context)
    return render(request, 'branch/branches.html', context)

@login_required
@access_level_required(['Admin'])
def update_branch(request, branch_id):
    branch = Branch.objects.get(id=branch_id)
    form = BranchForm(instance=branch)
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch details updated successfully')
            return redirect('branches')
    context = {
        'form': form
    }
    return render(request, 'branch/branch_detail.html', context)


@login_required
@access_level_required(['Admin', 'Manager', 'Team Manager'])
def team_overview(request):
    users = services.get_users(request)
    form = UserForm(request=request)

    if request.method == 'POST':
        form = UserForm(request.POST, request=request)
        branch_id = request.POST['branch']
        branch = Branch.objects.get(id=branch_id)
        if form.is_valid():
            user = form.save(commit=False)
            password = user.password
            # If the password is provided, we need to hash it before saving the user
            if password:
                user.set_password(password)
            with transaction.atomic():
                try:
                    user.save()
                    # Create a employee profile
                    employee = Employee(user=user, 
                                        branch=branch, 
                                        role=user.role,
                                        name=f"{user.first_name} {user.last_name}",
                                        email=user.email,
                                        created_by=request.user
                                    )
                    employee.save()
                except Exception as e:
                    print(e)
                    messages.error(request, 'An error occurred while creating user and employee profile.')
            messages.success(request, 'User created successfully.')
            return redirect('team_member')
    context = {
        'users': users,
        'form': form
    }
    return render(request, 'team_member/team.html', context=context)

@login_required
@access_level_required(['Admin', 'Manager', 'Team Manager'])
def update_user(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user, request=request)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Member details updated successfully')
            return redirect('team_member')
    else:
        form = UserUpdateForm(instance=user, request=request)
    context = {
        'form': form    
    }
    return render(request, 'team_member/update_member.html', context=context)

@login_required
@access_level_required(['Admin', 'Manager', 'Team Manager'])  
def edit_userprofile(request, employee_id):
    employee = Employee.objects.get(id=employee_id)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES,instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member details updated successfully')
            return redirect('team_member')
    else:
        form = EmployeeForm(instance=employee)
    context = {
        'form': form,
        'employee': employee
    }
    return render(request, 'team_member/member_detail.html', context=context)

    
@login_required
@access_level_required(['Admin', 'Manager', 'Team Manager'])
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    if user is not None:
        user.delete()
        messages.success(request, 'User deleted successfully.')
    else:
        messages.error(request, 'User not found.')
    return redirect('team_member') 

@login_required
def user_settings(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        form = UserSettingForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            print(request.POST)

            # If the password is provided, we need to hash it before saving the user
            new_password = request.POST['new_password']
            confirm_new_password = request.POST['confirm_new_password']

            if new_password and confirm_new_password and new_password == confirm_new_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully. Please login again.')
                return redirect('login')
            user.save()
            messages.success(request, 'Member details updated successfully')
            return redirect('dashboard')
    else:
        form = UserSettingForm(instance=user)
    context = {
        'form': form    
    }
    return render(request, 'team_member/settings.html', context=context)