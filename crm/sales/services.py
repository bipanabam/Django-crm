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
    
def get_client(request, client_id):
    branch = get_user_branch(request)
    return Client.objects.get(branch=branch, id=client_id)

def get_unassigned_clients(branch):
    clients = Client.objects.filter(branch=branch).order_by("-created_at")
    for client in clients:
        if client.is_assigned:
            clients = clients.exclude(id=client.id)
    return clients
