from django.urls import path

from . import views

urlpatterns = [
    path('', views.documentation_overview, name='documentation_overview'),
    path("country-wise-document/add/", views.country_wise_document_view, name="country_wise_documents"),
    path("applicant-document/edit/<int:country_id>/<int:document_id>/", views.edit_countrywise_client_document, name="edit_countrywise_client_document"),
    path("applicant-document/delete/<int:country_id>/<int:document_id>/", views.delete_countrywise_client_document, name="delete_countrywise_client_document"),
    path("country-wise-applicants/<int:country_id>/", views.country_wise_applicant_list, name="country_wise_applicants"),
    path("countries-required-documents/<int:country_id>/", views.country_wise_required_documents, name="countries_required_documents"),
    path("applicant-documents/<int:country_id>/<int:client_id>/", views.applicant_document, name='applicant_document'),
    path('ajax/get-document-types/', views.get_document_types, name='get_document_types'),
]
