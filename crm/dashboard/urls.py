from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path("sales/chart-data/", views.sales_chart_data, name="sales_chart_data"),
    path("revenue/chart-data/", views.revenue_chart_data, name="revenue_chart_data"),
    path('dashboard/partial/', views.admin_dashboard_partial, name='admin_dashboard_partial'),

]
