from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.forms import inlineformset_factory

from django.contrib.auth.decorators import login_required

from company.decorators import access_level_required

from .forms import CountryForm, DocumentTypeForm,DocumentFormSet, CountryWiseClientDocumentForm, CountryWiseClientDocumentFormSet, BaseCountryWiseClientDocumentFormSet
from .models import Country, CountryWiseClientDocument, DocumentType

from sales.models import ClientDocument

from company.services import get_user_branch
from .services import document_distinct_by_client, get_all_client_documents

# Create your views here.
@login_required
@access_level_required(['Admin', 'Manager'])
def country_wise_document_view(request):
    country_form = CountryForm()
    formset = DocumentFormSet()

    # Country wise document queryset
    branch = get_user_branch(request)
    countries = Country.objects.filter(branch=branch)

    if request.method == 'POST':
        country_form = CountryForm(request.POST)
        formset = DocumentFormSet(request.POST)

        print(formset.cleaned_data)

        if country_form.is_valid() and formset.is_valid():
            country = country_form.save(commit=False)
            country.branch = get_user_branch(request)
            country.save()
            formset.instance = country
            formset.save()
            messages.success(request, 'Country and document added successfully')
            return redirect('country_wise_documents')
        
    return render(request, 'documentation/country_wise_documents.html', {
        'country_form': country_form,
        'formset': formset,
        'countries': countries,
    })

@login_required
@access_level_required(['Admin', 'Manager'])
def edit_countrywise_document(request, country_id):
    branch = get_user_branch(request)
    country = get_object_or_404(Country, id=country_id, branch=branch)
    country_form = CountryForm(instance=country)
    formset_class = inlineformset_factory(
        Country, DocumentType, form=DocumentTypeForm,
        extra=0, can_delete=True
    )
    formset = formset_class(instance=country)

    if request.method == 'POST':
        country_form = CountryForm(request.POST, instance=country)
        formset = formset_class(request.POST, instance=country)

        if country_form.is_valid() and formset.is_valid():
            country_form.save()
            formset.save()
            messages.success(request, 'Country and document updated successfully')
            return redirect('country_wise_documents')
        else:
            print(country_form.errors)
            print(formset.errors)

    return render(request, 'documentation/form/edit_countrywise_document.html', {
        'country_form': country_form,    
        'formset': formset,
    })

@login_required
@access_level_required(['Admin', 'Manager'])
def delete_country(request, country_id):
    branch = get_user_branch(request)
    country = get_object_or_404(Country, id=country_id, branch=branch)
    
    if request.method == 'POST':
        country.delete()
        messages.success(request, "Country removed successfully.")
        return redirect('country_wise_documents') 
    return redirect('country_wise_documents')

@login_required
@access_level_required(['Admin', 'Manager', 'Counsellor', 'Sales Representative'])
def get_document_types(request):
    country_id = request.GET.get('country_id')
    if country_id:
        document_types = DocumentType.objects.filter(country_id=country_id).values('id', 'document_title')
        return JsonResponse({'document_types': list(document_types)})
    return JsonResponse({'document_types': []})


def get_client_documents(request):
    client_id = request.GET.get('client_id')
    documents = []

    if client_id:
        documents_qs = ClientDocument.objects.filter(client_id=client_id)
        for doc in documents_qs:
            documents.append({
                'document_type': doc.document_type,
                'document_file_url': doc.document.url,
            })

    return JsonResponse({'documents': documents})

@login_required
@access_level_required(['Admin', 'Manager', 'Counsellor', 'Sales Representative'])
def documentation_overview(request):
    branch = get_user_branch(request)
    countrywise_documentation = Country.objects.filter(branch=branch)
    countrywise_client_document = get_all_client_documents(request)

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

@login_required
@access_level_required(['Admin', 'Manager', 'Counsellor', 'Sales Representative'])
def edit_countrywise_client_document(request, country_id, document_id):
    branch = get_user_branch(request)
    country = get_object_or_404(Country, id=country_id, branch=branch)

    instance = CountryWiseClientDocument.objects.get(
        country=country, id=document_id
    )

    if request.method == 'POST':
        form = CountryWiseClientDocumentForm(request.POST, request.FILES, instance=instance, request=request)
        if form.is_valid():
            updated_document = form.save(commit=False)
            updated_document.save()
            messages.success(request, 'Document updated successfully.')
            return redirect('documentation_overview')
        else:
            print(form.errors)
            messages.error(request, 'There were errors in the form.')
    else:
        form = CountryWiseClientDocumentForm(instance=instance, request=request)

    return render(request, 'documentation/form/edit_countrywise_client_document.html', {
        'form': form,
        'country': country,
    })

@login_required
@access_level_required(['Admin', 'Manager', 'Counsellor', 'Sales Representative'])
def delete_countrywise_client_document(request, country_id, document_id):
    document = get_object_or_404(CountryWiseClientDocument, id=document_id, country_id=country_id)
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, "Document deleted successfully.")
        return redirect('documentation_overview') 
    
    return redirect('documentation_overview')

@login_required
@access_level_required(['Admin', 'Manager', 'Counsellor', 'Sales Representative'])
def country_wise_applicant_list(request, country_id):
    docs = CountryWiseClientDocument.objects.filter(
        country_id=country_id
        ).order_by('client') 
    applicants = document_distinct_by_client(docs)
    context = {
        'applicants': applicants,
        'country': Country.objects.get(id=country_id),
    }
    return render(request, 'documentation/country_wise_applicant.html', context=context)

@login_required
@access_level_required(['Admin', 'Manager', 'Counsellor', 'Sales Representative'])
def country_wise_required_documents(request, country_id):
    branch = get_user_branch(request)
    selected_country = Country.objects.get(id=country_id, branch=branch)
    documents = selected_country.documents.all()

    context = {
        'country': selected_country,
        'documents': documents,
    }
    return render(request, 'documentation/country_wise_required_documents.html', context=context)

@login_required
@access_level_required(['Admin', 'Manager', 'Counsellor', 'Sales Representative'])
def applicant_document(request, country_id, client_id):
    documents = CountryWiseClientDocument.objects.filter(client_id=client_id, country_id=country_id)
    context = {
        'documents': documents,
        'country': documents[0].country
    }

    return render(request, "documentation/applicant_documents.html", context=context)