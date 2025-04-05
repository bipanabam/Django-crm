from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import CountryForm, DocumentFormSet
from .models import Country

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


