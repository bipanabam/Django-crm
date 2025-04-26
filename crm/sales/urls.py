from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_view, name='sales'),
    path('inquiry/add/', views.inquiry_form_view, name='inquiry_form'),
    path('client/<int:client_id>/edit/', views.edit_client, name='edit_client'),
    path('client/<int:client_id>/delete/', views.delete_client, name='delete_client'),

    path('invoice/add/', views.create_invoice, name="create_invoice"),
    path('invoice/edit/<int:voucher_id>/', views.edit_invoice, name="edit_invoice"),
    path('invoice/delete/<int:voucher_id>/', views.delete_invoice, name="delete_invoice"),
    path('ajax/get-due-amount/', views.get_due_amount, name='get_due_amount'),
]
