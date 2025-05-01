from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User, AbstractUser, Group

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
  # email = models.EmailField(unique=True, blank=True, null=True)
  # phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
  country = models.CharField(max_length=100)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  def get_absolute_url(self):
    return reverse("branch_detail", kwargs={"pk": self.pk})
  
  def __str__(self):
    return f"{self.company.name} - {self.name}"

class AccessLevel(models.Model):
  name = models.CharField(max_length=100)

  def __str__(self):
    return self.name

class RoleChoices(models.TextChoices):
  ADMIN = 'admin', 'Admin'
  MANAGER = 'manager', 'Manager'
  TEAM_MANAGER = 'team manager', 'Team Manager'
  SALES_REPRESENTATIVE = 'sales representative', 'Sales Representative'
  COUNSELLOR = 'counsellor', 'Counsellor'
  MARKETING = 'marketing', 'Marketing'
  ACCOUNTANT = 'accountant', 'Accountant'
 
   
class User(AbstractUser):
  email = models.EmailField(unique=True)
  role = models.CharField(max_length=20, choices=RoleChoices, default=RoleChoices.ADMIN)

  access_level = models.ManyToManyField(AccessLevel, blank=True, related_name='users')

  online_status = models.CharField(max_length=10, choices=[('online', 'Online'), ('idle', 'Idle'), ('offline', 'Offline')], default='offline')
  last_seen = models.DateTimeField(null=True, blank=True)

  USERNAME_FIELD = 'email'  # Use email as the unique identifier for authentication
  REQUIRED_FIELDS = ['username'] 

  @property
  def last_active(self):
    if self.online_status == 'online':
      return "Active Now"
    else:
      from django.utils import timezone
      now = timezone.now()
      delta = now - self.last_seen
      return f"{int(delta.total_seconds() / 60)} mins ago"  # returns minutes as integer

  def __str__(self):
      return f"{self.username}"

class UserActivityLog(models.Model):
  STATUS_CHOICES = [
      ('online', 'Online'),
      ('idle', 'Idle'),
      ('offline', 'Offline'),
  ]

  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
  status = models.CharField(max_length=10, choices=STATUS_CHOICES)
  timestamp = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return f"{self.user.username} - {self.status} @ {self.timestamp}"

class Employee(models.Model):
  branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='employees')
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
  name = models.CharField(max_length=50, null=True, blank=True)
  email = models.EmailField(null=True, blank=True)
  phone_number = models.CharField(max_length=14, null=True, blank=True)
  role = models.CharField(max_length=15, null=True, blank=True)
  created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"{self.branch.name} - {self.user.username} ({self.user.role})"


