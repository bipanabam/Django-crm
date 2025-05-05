from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Demand

from .forms import DemandForm

from company.services import get_branches, get_user_branch


# Create your views here.
@login_required
def marketing_overview(request):
    branches = get_branches(request)
    demands = Demand.objects.filter(branch__in=branches)

    # Demand Pagination
    demand_paginator = Paginator(demands, 5)
    demand_page_number = request.GET.get('demand_page')
    demand_page_obj = demand_paginator.get_page(demand_page_number)

    context = {
        'demand_page_obj': demand_page_obj
    }

    return render(request, 'marketing/overview.html', context=context)

def create_demand(request):
    if request.method == 'POST':
        form = DemandForm(request.POST, request=request)
        if form.is_valid():
            demand = form.save(commit=False)
            demand.branch = request.user.profile.branch
            demand.created_by = request.user
            demand.save()
            messages.success(request, 'Demand created successfully')
            return redirect('marketing')
        else:
            return render(request, 'marketing/create_demand.html', {'form': form})
    else:
        form = DemandForm(request=request)
    return render(request, 'marketing/create_demand.html', {'form': form})

def edit_demand(request, demand_id):
    branch = get_user_branch(request)
    instance = get_object_or_404(Demand, id=demand_id, branch=branch)
    if request.method == 'POST':
        form = DemandForm(request.POST, request=request, instance=instance)
        if form.is_valid():
            demand = form.save(commit=False)
            demand.save()
            messages.success(request, 'Demand edited successfully')
            return redirect('marketing')
        else:
            return render(request, 'marketing/edit_demand.html', {'form': form})
    else:
        form = DemandForm(request=request, instance=instance)
    return render(request, 'marketing/edit_demand.html', {'form': form})

@login_required
def delete_demand(request, demand_id):
    branch = get_user_branch(request)
    demand = get_object_or_404(Demand, id=demand_id, branch=branch)
    
    if request.method == 'POST':
        demand.delete()
        messages.success(request, "Demand deleted successfully.")
        return redirect('marketing') 
    return redirect('marketing')
