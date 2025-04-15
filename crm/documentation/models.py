from django.db import models

from company.models import Branch, User

from sales.models import Client

# Create your models here.
class Country(models.Model):
    name = models.CharField(max_length=30)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="overseas")

    def __str__(self):
        return self.name

class DocumentType(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='documents')
    document_title = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.document_title}"
    
class CountryWiseClientDocument(models.Model):
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='countrywisedocument')
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True)
    document_file = models.ImageField(upload_to='country/client_documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
