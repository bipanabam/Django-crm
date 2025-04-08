from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_view, name='sales'),
    path('inquiry/add/', views.inquiry_form_view, name='inquiry_form'),
]
