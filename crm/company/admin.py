from django.contrib import admin
from .models import Company, Branch, User, Employee

# Register your models here.
admin.site.register(Company)
admin.site.register(Branch)
admin.site.register(User)
admin.site.register(Employee)