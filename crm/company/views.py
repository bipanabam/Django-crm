from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.views.generic import (CreateView, DetailView, UpdateView)

from .models import Branch, User, Employee
from .forms import BranchForm, UserForm

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
            form.save()
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

class UserCreateView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'user/add_user.html'
    success_url = reverse_lazy('add_user')

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
                employee = Employee(user=user, branch=branch)
                employee.save()
            except Exception as e:
                print(e)
                messages.error(self.request, 'An error occurred while creating user and employee profile.')
                return super().form_invalid(form)
        return super().form_valid(form)
        

