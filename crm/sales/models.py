from django.db import models

from company.models import User, Branch

# Create your models here.
class StatusChoices(models.TextChoices):
  PENDING = 'Pending', 'Pending'
  IN_PROGRESS = 'In Progress', 'In Progress'
  PAID = 'Paid', 'Paid'

class Client(models.Model):
  branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='clients')
  name = models.CharField(max_length=50)
  address = models.CharField(max_length=255)
  contact_number = models.CharField(max_length=14)
  email_address = models.EmailField()
  nationality = models.CharField(max_length=50)
  father_name = models.CharField(max_length=50)
  mother_name = models.CharField(max_length=50)
  preferred_country = models.CharField(max_length=150)
  visa_type = models.CharField(max_length=50)
  package_amount = models.DecimalField(max_digits=10, decimal_places=2)
  advance_paid = models.DecimalField(max_digits=10, decimal_places=2)
  due_amount = models.DecimalField(max_digits=10, decimal_places=2)
  more_remarks = models.TextField(null=True, blank=True)
  status = models.CharField(choices=StatusChoices, default=StatusChoices.PENDING, max_length=15)
  created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_client')
  assigned_date = models.DateTimeField(null=True, blank=True)

  @property
  def is_assigned(self):
    if self.assigned_to is not None:
      return True
    return False

  def __str__(self):
    return f"{self.name}"

class ClientDocument(models.Model):
  client = models.ForeignKey(Client, on_delete=models.CASCADE)
  document_type = models.CharField(max_length=250)
  document = models.ImageField(upload_to='client_documents/')
