from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from company.models import User, Branch
from company.services import get_user_branch

from django.utils import timezone

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
  status = models.CharField(choices=StatusChoices, default=StatusChoices.IN_PROGRESS, max_length=15)
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
  
  @property
  def has_dues(self):
    if self.due_amount > 0:
      return True
    return False


  def __str__(self):
    return f"{self.name}"

class ClientDocument(models.Model):
  client = models.ForeignKey(Client, on_delete=models.CASCADE)
  document_type = models.CharField(max_length=250)
  document = models.ImageField(upload_to='client_documents/')


class VoucherStatusChoices(models.TextChoices):
  PENDING = 'Pending', 'Pending'
  PAID = 'Paid', 'Paid'

class Voucher(models.Model):
  VOUCHER_TYPE_CHOICES = [
      ('Payment', 'Payment'),
      ('Receipt', 'Receipt'),
      ('Journal', 'Journal'),
      ('Other', 'Other'),
  ]

  VOUCHER_CATEGORY_CHOICES = [
      ('Sales', 'Sales'),
      ('Service', 'Service'),
      ('Salary', 'Salary'),
      ('Manual', 'Manual'),
  ]

  VOUCHER_STATUS_CHOICES = [
      ('Pending', 'Pending'),
      ('Paid', 'Paid'),
      ('Rejected', 'Rejected'),
      ('Cancelled', 'Cancelled'),
  ]

  PAYMENT_METHOD_CHOICES = [
      ('Cash', 'Cash'),
      ('Bank', 'Bank'),
      ('Online', 'Online'),
      ('Cheque', 'Cheque'),
  ]
  branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='vouchers')

  invoice_number = models.CharField(max_length=50, null=True, blank=True, unique=True)
  type = models.CharField(max_length=50, choices=VOUCHER_TYPE_CHOICES)
  category = models.CharField(max_length=50, choices=VOUCHER_CATEGORY_CHOICES)

  # generic foreign key fields
  account_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
  account_id = models.PositiveIntegerField(null=True)
  account = GenericForeignKey('account_type', 'account_id')

  amount = models.DecimalField(max_digits=10, decimal_places=2)
  narration = models.TextField(null=True, blank=True)
  payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)

  created_at = models.DateTimeField(auto_now_add=True)
  created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_vouchers")
  updated_at = models.DateTimeField(auto_now=True)
  updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="updated_vouchers")

  status = models.CharField(max_length=20, choices=VOUCHER_STATUS_CHOICES, default='Pending')

  def save(self, *args, **kwargs):
    # Generate invoice_number if it doesn't already exist
    if not self.invoice_number:
        self.invoice_number = self.generate_invoice_number()
    super().save(*args, **kwargs)
    
  def generate_invoice_number(self):
    branch = self.branch
    today_str = timezone.now().strftime('%Y%m%d')
    last_voucher = Voucher.objects.filter(created_at__date=timezone.now().date(), branch=branch).order_by('invoice_number').last()
    if last_voucher:
      last_sequence = int(last_voucher.invoice_number[-3:])
      next_sequence = last_sequence + 1
    else:
      next_sequence = 1
    return f"{today_str}{next_sequence:03}"
      
  def __str__(self):
    return f"{self.type.capitalize()} : {self.category} #{self.invoice_number}"

