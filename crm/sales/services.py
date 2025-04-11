from .models import Client
from company.services import get_user_branch, get_branches

def get_all_clients(request):
    user = request.user
    if user.role == 'admin':
        branches = get_branches(request)
        return Client.objects.filter(branch__in=branches)
    else:
        branch = get_user_branch(request)
        return Client.objects.filter(branch=branch)