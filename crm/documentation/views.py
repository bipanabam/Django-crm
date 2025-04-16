from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction

from .forms import CountryForm, DocumentFormSet, CountryWiseClientDocumentFormSet
from .models import Country, CountryWiseClientDocument, DocumentType

from company.services import get_user_branch

# Create your views here.
def country_wise_document_view(request):
    country_form = CountryForm()
    formset = DocumentFormSet()

    # Country wise document queryset
    country_wise_documents = Country.objects.all()

    if request.method == 'POST':
        country_form = CountryForm(request.POST)
        formset = DocumentFormSet(request.POST)

        if country_form.is_valid() and formset.is_valid():
            country = country_form.save(commit=False)
            country.branch = get_user_branch(request)
            country.save()
            formset.instance = country
            formset.save()
            messages.success(request, 'Document added successfully')
            return redirect('country_wise_documents')
        
    return render(request, 'documentation/country_wise_documents.html', {
        'country_form': country_form,
        'formset': formset,
        'country_wise_documents': country_wise_documents,
    })

def get_document_types(request):
    country_id = request.GET.get('country_id')
    if country_id:
        document_types = DocumentType.objects.filter(country_id=country_id).values('id', 'document_title')
        return JsonResponse({'document_types': list(document_types)})
    return JsonResponse({'document_types': []})

def documentation_overview(request):
    branch = get_user_branch(request)
    countrywise_documentation = Country.objects.filter(branch=branch)
    countrywise_client_document = CountryWiseClientDocument.objects.filter(country__branch=branch)

    # client document form
    if request.method == 'POST':
        formset = CountryWiseClientDocumentFormSet(request.POST, request.FILES, queryset=CountryWiseClientDocument.objects.none(), form_kwargs={'request': request})
        if formset.is_valid():
            instances = formset.save(commit=False)
            with transaction.atomic():
                for instance in instances:
                    instance.uploaded_by = request.user
                    instance.save()
            messages.success(request, 'Document added successfully')
            return redirect('documentation_overview')
        else:
            print(formset.errors)
            formset = CountryWiseClientDocumentFormSet(request.POST, request.FILES, queryset=CountryWiseClientDocument.objects.none(), form_kwargs={'request': request})
    else:
        formset = CountryWiseClientDocumentFormSet(queryset=CountryWiseClientDocument.objects.none(), form_kwargs={'request': request})

    context = {
        'countries_documentation': countrywise_documentation,
        'formset': formset,
        'countrywise_client_document': countrywise_client_document,
    }
    return render(request, 'documentation/overview.html', context=context)

def country_wise_applicant_view(request, country_id):
    applicants = CountryWiseClientDocument.objects.filter(
        country_id=country_id
        )
    context = {
        'applicants': applicants,
        'country': Country.objects.get(id=country_id),
    }
    return render(request, 'documentation/country_wise_applicant.html', context=context)

def country_wise_required_documents(request, country_id):
    branch = get_user_branch(request)
    selected_country = Country.objects.get(id=country_id, branch=branch)
    documents = selected_country.documents.all()

    context = {
        'country': selected_country,
        'documents': documents,
    }
    return render(request, 'documentation/country_wise_required_documents.html', context=context)

def applicant_document(request, client_id):
    documents = CountryWiseClientDocument.objects.filter(client_id=client_id)
    context = {
        'documents': documents,
        'country': documents[0].country
    }

    return render(request, "documentation/applicant_documents.html", context=context)