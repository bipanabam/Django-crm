from django.urls import path

from . import views

urlpatterns = [
    path('', views.marketing_overview, name='marketing'),
]