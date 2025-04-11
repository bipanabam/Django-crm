from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

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
            print(formset.cleaned_data)
            for instance in instances:
                print(instance)
            # for instance in instances:
            #         instance.client = client
            #         instance.country = country
            #         instance.save()
            return redirect('documentation_overview')
        else:
            print(formset.errors)
    else:
        formset = CountryWiseClientDocumentFormSet(queryset=CountryWiseClientDocument.objects.none(), form_kwargs={'request': request})

    context = {
        'countries_documentation': countrywise_documentation,
        'formset': formset,
        'countrywise_client_document': countrywise_client_document,
    }
    return render(request, 'documentation/overview.html', context=context)

# def upload_documents(request, client_id):
#     client = Client.objects.get(id=client_id)
#     country = client.country  # Assuming client has a related country

#     if request.method == 'POST':
#         formset = CountryWiseClientDocumentFormSet(request.POST, request.FILES, queryset=CountryWiseClientDocument.objects.none())
#         if formset.is_valid():
#             instances = formset.save(commit=False)
#             for instance in instances:
#                 instance.client = client
#                 instance.country = country
#                 instance.save()
#             return redirect('some_success_page')
#     else:
#         formset = CountryWiseClientDocumentFormSet(queryset=CountryWiseClientDocument.objects.none())

#     return render(request, 'upload_documents.html', {
#         'formset': formset,
#         'client': client,
#         'country': country,
#     })
