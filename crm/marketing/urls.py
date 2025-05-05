from django.urls import path

from . import views

urlpatterns = [
    path('', views.marketing_overview, name='marketing'),
    path('demand/create/', views.create_demand, name='create_demand'),
    path('demand/<int:demand_id>/edit/', views.edit_demand, name='edit_demand'),
    path('demand/<int:demand_id>/delete/', views.delete_demand, name='delete_demand'),
]