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

class CampaignPlateformChoices(models.TextChoices):
  FACEBOOK = 'Facebook', 'Facebook'

class CampaignStatus(models.TextChoices):
  DRAFT = 'Draft', 'Draft'
  RUNNING = 'Running', 'Running'
  PAUSED = 'Paused', 'Paused'

class Campaign(models.Model):
  name = models.CharField(max_length=100)
  plateform = models.CharField(max_length=15, choices=CampaignPlateformChoices.choices)
  budget = models.DecimalField(max_digits=10, decimal_places=2)
  status = models.CharField(max_length=15, choices=CampaignStatus.choices, default=CampaignStatus.DRAFT)
  created_at = models.DateTimeField(auto_now_add=True)
  created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  updated_at = models.DateTimeField(auto_now=True)

  fb_campaign_id = models.CharField(max_length=50, blank=True, null=True)

  branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="campaigns")

  def __str__(self):
    return f"{self.name} ({self.plateform})"

class AdSet(models.Model):
  campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='adsets')
  name = models.CharField(max_length=100)
  daily_budget = models.DecimalField(max_digits=10, decimal_places=2)
  optimization_goal = models.CharField(max_length=50)
  billing_event = models.CharField(max_length=50)
  bid_strategy = models.CharField(max_length=50)
  fb_adset_id = models.CharField(max_length=100, blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

class AdCreative(models.Model):
  campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='creatives')
  name = models.CharField(max_length=100)
  message = models.TextField()
  link = models.URLField()
  call_to_action = models.CharField(max_length=50, default='LEARN_MORE')
  fb_creative_id = models.CharField(max_length=100, blank=True, null=True)
  image = models.ImageField(upload_to='ad_creatives/', blank=True, null=True)
  image_hash = models.CharField(max_length=100, blank=True, null=True) 
  created_at = models.DateTimeField(auto_now_add=True)

class Ad(models.Model):
  campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='ads')
  adset = models.ForeignKey(AdSet, on_delete=models.SET_NULL, null=True)
  creative = models.ForeignKey(AdCreative, on_delete=models.SET_NULL, null=True)
  name = models.CharField(max_length=100)
  fb_ad_id = models.CharField(max_length=100, blank=True, null=True)
  status = models.CharField(max_length=50, default='PAUSED')
  created_at = models.DateTimeField(auto_now_add=True)
