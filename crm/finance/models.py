from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from sales.models import Voucher

# Create your models here.
class JournalEntry(models.Model):
  voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='journal_entries')

  account_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
  account_id = models.PositiveIntegerField(null=True)
  account = GenericForeignKey('account_type', 'account_id')

  debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
  credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
  entry_date = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
      return f"{self.account_type.capitalize()} - Dr: {self.debit} Cr: {self.credit}"
