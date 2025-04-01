from django.urls import path
from . import views

urlpatterns = [
    path('branch/', views.branch_view, name='branches'),
   path('branch/<int:pk>/', views.BranchUpdateView.as_view(), name='branch_detail'),
   
   path('user/add/', views.UserCreateView.as_view(), name='add_user'),
]
