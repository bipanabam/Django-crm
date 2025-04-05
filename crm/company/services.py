from .models import Branch, User


def get_branches(request):
    user = request.user
    company = user.profile.branch.company
    branches = Branch.objects.filter(company=company)
    if user.role == 'admin':
        return branches
    elif user.role in ['manager', 'accountant']:
        return branches.filter(id=user.profile.branch.id)
    else:
        return Branch.objects.none()
    
def get_user_branch(request):
    user = request.user
    branch = user.profile.branch
    return branch
    
def get_users(request):
    user = request.user
    company = user.profile.branch.company
    branch = user.profile.branch
    if user.role == 'admin':
        return User.objects.filter(profile__branch__company=company)
    elif user.role in ['manager', 'accountant']:
        return User.objects.filter(profile__branch=branch)
    else:
        return User.objects.none()