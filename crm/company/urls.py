from django.urls import path
from . import views

urlpatterns = [
    path('branch/', views.branch_view, name='branches'),
   path('branch/<int:branch_id>/', views.update_branch, name='branch_detail'),

   path('team-member/', views.team_overview, name='team_member'),
   path('team-member/update/<int:user_id>/', views.update_user, name='update_member'),
   path('team-member/<int:employee_id>/', views.edit_userprofile, name='member_detail'),
   path('team-member/delete/<int:user_id>/', views.delete_user, name='delete_member'),
]
