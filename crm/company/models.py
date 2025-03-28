from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User, AbstractUser

# Create your models here.
class Company(models.Model):
   name = models.CharField(max_length=255, unique=True)
   email = models.EmailField(unique=True, blank=True, null=True)
   phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
   country = models.CharField(max_length=100, blank=True, null=True)
   city = models.CharField(max_length=100, blank=True, null=True)
   address = models.TextField(blank=True, null=True)
   postal_code = models.CharField(max_length=20, blank=True, null=True)
   website = models.URLField(blank=True, null=True)
   established_date = models.DateField(blank=True, null=True)
   logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   class Meta:
     verbose_name = 'Company'
     verbose_name_plural = 'Companies'

   def __str__(self):
     return self.name
  

class Branch(models.Model):
  company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='branches')
  name = models.CharField(max_length=255)
  email = models.EmailField(unique=True, blank=True, null=True)
  phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
  country = models.CharField(max_length=100)
  city = models.CharField(max_length=100, blank=True, null=True)
  address = models.TextField()
  postal_code = models.CharField(max_length=20)

  def get_absolute_url(self):
    return reverse("branch_detail", kwargs={"pk": self.pk})
  
  def __str__(self):
    return f"{self.company.name} - {self.name}"

class RoleChoices(models.TextChoices):
  ADMIN = 'admin', 'Admin'
  MANAGER = 'manager', 'Manager'
  ACCOUNTANT = 'accountant', 'Accountant'
   
class User(AbstractUser):
  role = models.CharField(max_length=10, choices=RoleChoices, default=RoleChoices.ACCOUNTANT)

  def __str__(self):
      return f"{self.username}"

class Employee(models.Model):
  branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='employees')
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

  def __str__(self):
    return f"{self.branch.company.name} - {self.branch.name} - {self.user.username} ({self.user.role})"


