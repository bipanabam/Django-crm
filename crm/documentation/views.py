from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.forms import modelformset_factory

from .forms import CountryForm, DocumentFormSet, CountryWiseClientDocumentForm, CountryWiseClientDocumentFormSet, BaseCountryWiseClientDocumentFormSet
from .models import Country, CountryWiseClientDocument, DocumentType

from company.services import get_user_branch
from .services import document_distinct_by_client

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

# def edit_countrywise_client_document(request, country_id, client_id):
#     branch = get_user_branch(request)
#     country = get_object_or_404(Country, id=country_id, branch=branch)

#     queryset = CountryWiseClientDocument.objects.filter(
#         country=country, client_id=client_id
#     )

#     formset_class =  modelformset_factory(
#         CountryWiseClientDocument,
#         form=CountryWiseClientDocumentForm,
#         formset=BaseCountryWiseClientDocumentFormSet,
#         extra=0,  # number of empty forms shown by default
#         can_delete=True  # allows deletion of entries
#     )

#     if request.method == 'POST':
#         formset = formset_class(request.POST, request.FILES, queryset=queryset, form_kwargs={'request': request})
#         if formset.is_valid():
#             with transaction.atomic():
#                 instances = formset.save(commit=False)
#                 for instance in instances:
#                     instance.uploaded_by = request.user
#                     instance.country = country
#                     instance.client_id = client_id
#                     instance.save()
#                 for obj in formset.deleted_objects:
#                     obj.delete()
#             messages.success(request, 'Documents updated successfully.')
#             return redirect('documentation_overview')
#         else:
#             print(formset.errors)
#             messages.error(request, 'There were errors in the form.')
#     else:
#         formset = formset_class(queryset=queryset, form_kwargs={'request': request})

#     return render(request, 'documentation/form/edit_countrywise_client_document.html', {
#         'formset': formset,
#         'country': country,
#         'client_id': client_id,
#     })

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

def country_wise_required_documents(request, country_id):
    branch = get_user_branch(request)
    selected_country = Country.objects.get(id=country_id, branch=branch)
    documents = selected_country.documents.all()

    context = {
        'country': selected_country,
        'documents': documents,
    }
    return render(request, 'documentation/country_wise_required_documents.html', context=context)

def applicant_document(request, country_id, client_id):
    documents = CountryWiseClientDocument.objects.filter(client_id=client_id, country_id=country_id)
    context = {
        'documents': documents,
        'country': documents[0].country
    }

    return render(request, "documentation/applicant_documents.html", context=context)