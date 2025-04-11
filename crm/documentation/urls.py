from django.urls import path

from . import views

urlpatterns = [
    path("country-wise-document/", views.country_wise_document_view, name="country_wise_documents"),
    path('', views.documentation_overview, name='documentation_overview'),
    path('ajax/get-document-types/', views.get_document_types, name='get_document_types'),
]
