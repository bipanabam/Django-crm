from .models import Client
from company.services import get_user_branch, get_branches


def get_branch_clients(request):
    branch = get_user_branch(request)
    return Client.objects.filter(branch=branch)

def get_all_clients(request):
    branches = get_branches(request)
    return Client.objects.filter(branch__in=branches)