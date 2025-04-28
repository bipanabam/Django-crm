from django.urls import path
from . import views

urlpatterns = [
    path("", views.account_overview, name="account_overview"),
    path('voucher/<int:voucher_id>/approve/', views.approve_voucher, name='approve_voucher'),
    path('voucher/add/', views.create_voucher, name="create_voucher"),
    path('voucher/edit/<int:voucher_id>/', views.edit_voucher, name="edit_voucher"),
    path('voucher/delete/<int:voucher_id>/', views.delete_voucher, name="delete_voucher"),
    path('ajax/get-accounts/', views.get_accounts_by_type, name='get_accounts_by_type'),

    path('voucher/<int:voucher_id>/bill/', views.invoice_bill_view, name='invoice_bill'),
]