from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Campaign
from marketing.tasks import create_ads_async

# @receiver(post_save, sender=Campaign)
# def trigger_facebook_ad_creation(sender, instance, created, **kwargs):
#     if created and instance.plateform == 'Facebook':
#         transaction.on_commit(lambda: create_facebook_ads_async.delay(campaign.id))
#         print('Campaign created')