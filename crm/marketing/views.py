from django.shortcuts import render

# Create your views here.
def marketing_overview(request):
    return render(request, 'marketing/overview.html')
