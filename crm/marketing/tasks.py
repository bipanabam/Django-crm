from celery import shared_task
from .services import create_full_facebook_ad_flow
from .models import Campaign

@shared_task
def create_ads_async(campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    if campaign.plateform == 'Facebook':
        result = create_full_facebook_ad_flow(campaign_id)

    if result:
        print("All done!", result)
    else:
        print("Something went wrong:")