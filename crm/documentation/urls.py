from django.urls import path

from . import views

urlpatterns = [
    path("country-wise-document/", views.country_wise_document_view, name="country_wise_documents"),
]
