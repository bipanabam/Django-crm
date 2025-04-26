from django.contrib.contenttypes.models import ContentType

from .models import Client, Voucher
from company.services import get_user_branch, get_branches

def get_all_clients(request):
    user = request.user
    if user.is_superuser:
        return Client.objects.all()
        
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

def get_assigned_clients(request):
    branch = get_user_branch(request)
    clients = Client.objects.filter(branch=branch, assigned_to=request.user).order_by("-created_at")
    return clients

def get_client_with_remaining_dues(request):
    clients = get_all_clients(request)
    for client in clients:
        if not client.has_dues:
            clients = clients.exclude(id=client.id)
    return clients

def get_all_vouchers(request):
    user = request.user
    if user.is_superuser:
        return Voucher.objects.all()
    if user.role == "admin":
        branches =  get_branches(request)
        vouchers = Voucher.objects.filter(branch__in=branches)
    else:
        branch = get_user_branch(request)
        vouchers = Voucher.objects.filter(branch=branch)
    return vouchers

def get_all_client_vouchers(request):
    client_type = ContentType.objects.get_for_model(Client)
    user = request.user
    if user.is_superuser:
        return Voucher.objects.all(account_type=client_type)
    if user.role == "admin":
        branches =  get_branches(request)
        vouchers = Voucher.objects.filter(branch__in=branches, account_type=client_type)
    else:
        branch = get_user_branch(request)
        vouchers = Voucher.objects.filter(branch=branch, account_type=client_type)
    return vouchers
    
