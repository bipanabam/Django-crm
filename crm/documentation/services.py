from .models import Country, CountryWiseClientDocument

from company.services import get_user_branch, get_branches

from sales.services import get_assigned_clients

def get_all_countries(request):
    if request.user.role == 'admin':
        branches = get_branches(request)
        return Country.objects.filter(branch__in=branches)
    else:
        branch = get_user_branch(request)
        return Country.objects.filter(branch=branch)

def get_client_documents(request):
    branches = get_branches(request)
    documents =  CountryWiseClientDocument.objects.filter(country__branch__in=branches)
    if request.user.role == 'sales representative':
        clients = get_assigned_clients(request)
        documents = documents.filter(client__in=clients)
    return documents

def document_distinct_by_client(docs):
    applicants = []
    seen_clients = set()
    for doc in docs:
        if doc.client_id not in seen_clients:
            seen_clients.add(doc.client_id)
            applicants.append(doc)
    return applicants
