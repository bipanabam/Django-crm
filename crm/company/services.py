from .models import Branch, User, Employee
from django.contrib.auth.models import Group


def get_branches(request):
    user = request.user
    if user.is_superuser:
        return Branch.objects.all()
    company = user.profile.branch.company
    branches = Branch.objects.filter(company=company)
    if user.role == 'admin':
        return branches
    else:
        return branches.filter(id=user.profile.branch.id)
    
def get_user_branch(request):
    user = request.user
    branch = user.profile.branch
    return branch
    
def get_users(request):
    if request.user.is_superuser:
        return User.objects.filter(is_superuser=False)
    user = request.user
    company = user.profile.branch.company
    branch = user.profile.branch
    if user.role == 'admin':
        return User.objects.filter(profile__branch__company=company)
    elif user.role == 'manager':
        return User.objects.filter(profile__branch=branch)
    else:
        return User.objects.filter(profile__branch=branch).exclude(role="manager")

def get_employees(request):
    user = request.user
    if user.is_superuser:
        return Employee.objects.all()
    company = user.profile.branch.company
    branch = user.profile.branch
    if user.role == 'admin':
        return Employee.objects.filter(branch__company=company)
    else:
        return Employee.objects.filter(branch=branch)


def get_all_access_levels(request):
    user = request.user
    if user.is_superuser:
        return Group.objects.all()

    if user.role == 'admin' or user.role == 'manager':
        return Group.objects.exclude(name='Admin')
    elif user.role == 'team manager':
        return Group.objects.exclude(name__in=['Admin', 'Manager'])
    else:
        return Group.objects.none()
    