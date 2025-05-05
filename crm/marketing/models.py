from django.db import models

from company.models import Branch, User
from documentation.models import Country

# Create your models here.
class DemandUrgencyChoices(models.TextChoices):
  URGENT = 'Urgent', 'Urgent'

class Demand(models.Model):
  country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="demands")
  job_name = models.CharField(max_length=100)
  no_of_vacancy = models.IntegerField()
  skill_required = models.TextField()
  # salary_offered = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  # Salary Range
  salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

  demand_urgency = models.CharField(max_length=10, choices=DemandUrgencyChoices.choices)
  created_at = models.DateTimeField(auto_now_add=True)
  created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  updated_at = models.DateTimeField(auto_now=True)

  branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="demands")

  @property
  def salary_range_display(self):
    if self.salary_min and self.salary_max:
        return f"{self.salary_min} - {self.salary_max}"
    elif self.salary_min:
        return f"From {self.salary_min}"
    elif self.salary_max:
        return f"Up to {self.salary_max}"
    return "Not specified"

  def __str__(self):
    return f"{self.job_name} ({self.no_of_vacancy})"

  class Meta:
    ordering = ['-created_at']