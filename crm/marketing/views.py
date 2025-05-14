from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction

from .models import Demand, Campaign

from .forms import DemandForm, CampaignForm, AdCreativeForm

from company.services import get_branches, get_user_branch

from .tasks import create_ads_async


# Create your views here.
@login_required
def marketing_overview(request):
    branches = get_branches(request)
    demands = Demand.objects.filter(branch__in=branches)
    campaigns = Campaign.objects.filter(branch__in=branches).order_by('-created_at')

    # Demand Pagination
    demand_paginator = Paginator(demands, 5)
    demand_page_number = request.GET.get('demand_page')
    demand_page_obj = demand_paginator.get_page(demand_page_number)

    # Campaign Pagination
    campaign_paginator = Paginator(campaigns, 5)
    campaign_page_number = request.GET.get('campaign_page')
    campaign_page_obj = campaign_paginator.get_page(campaign_page_number)

    # Form
    campaign_form = CampaignForm()
    adcreative_form = AdCreativeForm()

    if request.method == 'POST':
        campaign_form = CampaignForm(request.POST)
        adcreative_form = AdCreativeForm(request.POST, request.FILES)
        if campaign_form.is_valid() and adcreative_form.is_valid():
            print(campaign_form.cleaned_data)
            print(adcreative_form.cleaned_data)
            with transaction.atomic():
                try:
                    campaign = campaign_form.save(commit=False)
                    campaign.branch = request.user.profile.branch
                    campaign.created_by = request.user
                    campaign.save()
                    print(campaign)

                    adcreative = adcreative_form.save(commit=False)
                    adcreative.campaign = campaign
                    adcreative.save()
                    print(adcreative)

                    transaction.on_commit(lambda: create_ads_async.delay(campaign.id))
                except Exception as e:
                    print(e)
            messages.success(request, 'Campaign created successfully')
            return redirect('marketing')

    context = {
        'demand_page_obj': demand_page_obj,
        'campaign_page_obj': campaign_page_obj,
        'campaign_form': campaign_form,
        'adcreative_form': adcreative_form
    }

    return render(request, 'marketing/overview.html', context=context)

@login_required
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

@login_required
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

@login_required
def create_campaign(request):
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
