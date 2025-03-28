from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.views.generic import (CreateView, DetailView, ListView)

from .models import Branch, User, Employee
from .forms import BranchForm, UserForm

# Create your views here.
class BranchCreateView(CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'branch/create_branch.html'

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

class BranchDetailView(DetailView):
    model = Branch
    template_name = 'branch/branch_detail.html'
    context_object_name = 'branch'

class BranchListView(ListView):
    model = Branch
    template_name = 'branch/branch_list.html'
    context_object_name = 'branches'

class UserCreateView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'user/add_user.html'
    success_url = reverse_lazy('add_user')

    def form_valid(self, form):
        branch = form.cleaned_data['branch']
        print(f"Branch: {branch}")
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
        

