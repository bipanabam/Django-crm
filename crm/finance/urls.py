from django.urls import path
from . import views

urlpatterns = [
    path("", views.account_overview, name="account_overview"),
    path('voucher/<int:voucher_id>/approve/', views.approve_voucher, name='approve_voucher'),
]