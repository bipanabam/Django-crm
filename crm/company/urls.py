from django.urls import path
from . import views

urlpatterns = [
    path('branch/', views.branch_view, name='branches'),
   path('branch/<int:pk>/', views.BranchUpdateView.as_view(), name='branch_detail'),

   path('team-member/', views.MemberCreateView.as_view(), name='team_member'),
   path('team-member/<int:pk>/update/', views.MemberUpdateView.as_view(), name='update_member'),
   path('team-member/<int:pk>/', views.MemberDetailView.as_view(), name='member_detail'),
]
