from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Company, Branch, User, AccessLevel, Employee

# Register your models here.
class UserAdmin(BaseUserAdmin):
    model = User
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Access Control", {"fields": ("access_level",)}),
    )
    filter_horizontal = ("access_level",)  # to show it as a multiselect box

admin.site.register(User, UserAdmin)
admin.site.register(AccessLevel)
admin.site.register(Company)
admin.site.register(Branch)
admin.site.register(Employee)