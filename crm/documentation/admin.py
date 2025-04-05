from django.contrib import admin

from .models import Country, DocumentType

# Register your models here.
admin.site.register(Country)
admin.site.register(DocumentType)