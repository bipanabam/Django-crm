from django.urls import path

from . import views

urlpatterns = [
    path("country-wise-document/add/", views.country_wise_document_view, name="country_wise_documents"),
    path("country-wise-applicants/<int:country_id>/", views.country_wise_applicant_view, name="country_wise_applicants"),
    path("countries-required-documents/<int:country_id>/", views.country_wise_required_documents, name="countries_required_documents"),
    path('', views.documentation_overview, name='documentation_overview'),
    path('ajax/get-document-types/', views.get_document_types, name='get_document_types'),
]
