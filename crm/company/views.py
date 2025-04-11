from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.views.generic import (CreateView, DetailView, UpdateView)

from .models import Branch, User, Employee
from .forms import BranchForm, UserForm, UserUpdateForm, EmployeeForm
from . import services

# Create your views here.
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

class BranchUpdateView(UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = 'branch/branch_detail.html'

    def form_valid(self, form):
        messages.success(self.request, 'Branch details updated successfully')
        return super().form_valid(form)

class MemberCreateView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'team_member/team.html'
    success_url = reverse_lazy('team_member')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = services.get_users(self.request)
        return context

    def form_valid(self, form):
        branch = form.cleaned_data['branch']
        password = form.cleaned_data['password'] 
        # If the password is provided, we need to hash it before saving the user
        if password:
            form.instance.set_password(password)
        with transaction.atomic():
            try:
                user = form.save(commit=False)
                user.save()
                # Create a employee profile
                employee = Employee(user=user, 
                                    branch=branch, 
                                    role=user.role,
                                    name=f"{user.first_name} {user.last_name}",
                                    email=user.email
                                )
                employee.save()
            except Exception as e:
                print(e)
                messages.error(self.request, 'An error occurred while creating user and employee profile.')
                return super().form_invalid(form)
        messages.success(self.request, 'User created successfully.')
        return super().form_valid(form)
    
class MemberUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'team_member/update_member.html'
    success_url = reverse_lazy('team_member')

    def form_valid(self, form):
        messages.success(self.request, 'Member details updated successfully')
        return super().form_valid(form)
    
class MemberDetailView(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'team_member/member_detail.html'
    success_url = reverse_lazy('team_member')

    def form_valid(self, form):
        messages.success(self.request, 'Member details updated successfully')
        return super().form_valid(form)
    
        