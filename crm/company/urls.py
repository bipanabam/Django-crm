from django.urls import path
from . import views

urlpatterns = [
   path('branch/create/', views.BranchCreateView.as_view(), name='create_branch'),
   path('branch/<int:pk>/', views.BranchDetailView.as_view(), name='branch_detail'),
   path('branch/list/', views.BranchListView.as_view(), name='branches'),
   path('user/add/', views.UserCreateView.as_view(), name='add_user'),
]
