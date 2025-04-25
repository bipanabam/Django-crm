from company.models import Branch
from company.services import get_branches

def user_branch_data(request):
    user = request.user
    if user.is_authenticated:
        if user.is_superuser:
            branches = Branch.objects.all()
            selected_branch = None
        elif user.role == 'admin':
            branches = get_branches(request)
            selected_branch = None
        else:
            branches = Branch.objects.filter(id=user.profile.branch.id)  # Non-admin users see their own branch
            selected_branch = user.profile.branch

        return {
            'branches': branches,
            'selected_branch': selected_branch,
            'is_admin': user.is_superuser or user.role == 'admin',
        }
    return {}
