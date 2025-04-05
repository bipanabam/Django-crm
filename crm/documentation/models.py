from django.db import models

from company.models import Branch

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
        return f"{self.country.name} - {self.document_title}"
