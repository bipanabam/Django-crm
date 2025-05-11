import requests
from decouple import config
import json
from .models import Campaign, AdSet, AdCreative, Ad

# APP_ID = config('APP_ID')
# APP_SECRET = config('APP_SECRET')
ACCESS_TOKEN = config('ACCESS_TOKEN')
ACCOUNT_ID = config('AD_ACCOUNT_ID')
PAGE_ID = '277723765433874'

AD_ACCOUNT_ID = f'act_{ACCOUNT_ID}'

def create_full_facebook_ad_flow(campaign_id):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        adcreative = AdCreative.objects.get(campaign=campaign)

        # 1. Create Campaign
        campaign_url = f'https://graph.facebook.com/v22.0/{AD_ACCOUNT_ID}/campaigns'
        campaign_payload = {
            'name': campaign.name,
            'objective': 'OUTCOME_LEADS',
            'status': 'PAUSED',
            'special_ad_categories': ['NONE'],
            'access_token': ACCESS_TOKEN
        }
        r1 = requests.post(campaign_url, data=campaign_payload).json()
        campaign.fb_campaign_id = r1.get('id')
        campaign.save()
        print(r1)

        # 2. Create Ad Set
        adset_url = f'https://graph.facebook.com/v22.0/{AD_ACCOUNT_ID}/adsets'
        adset_payload = {
            'name': 'My Ad Set',
            'campaign_id': campaign.fb_campaign_id,
            'daily_budget': int(campaign.budget * 100),  # Convert to minor units
            'billing_event': 'IMPRESSIONS',
            'optimization_goal': 'REACH',
            'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
            'promoted_object': json.dumps({'page_id': PAGE_ID}),
            'targeting': json.dumps({"geo_locations": {"countries": ["US"]}}),
            'status': 'PAUSED',
            'access_token': ACCESS_TOKEN
        }

        r2 = requests.post(adset_url, data=adset_payload).json()
        print(r2)
        adset = AdSet.objects.create(
            campaign=campaign,
            name='My Ad Set',
            daily_budget=campaign.budget,
            optimization_goal='REACH',
            billing_event='IMPRESSIONS',
            bid_strategy='LOWEST_COST_WITHOUT_CAP',
            fb_adset_id=r2.get('id')
        )

        # Upload image to Facebook
        image_path = adcreative.image.path
        upload_url = f"https://graph.facebook.com/v22.0/{AD_ACCOUNT_ID}/adimages"

        with open(image_path, 'rb') as img_file:
            files = {'filename': img_file}
            params = {'access_token': ACCESS_TOKEN}
            response = requests.post(upload_url, files=files, data=params)
            image_data = response.json()

        # Get the hash
        image_hash = list(image_data['images'].values())[0]['hash']
        print("Image hash:", image_hash)

        # 3. Create Ad Creative
        creative_url = f"https://graph.facebook.com/v22.0/{AD_ACCOUNT_ID}/adcreatives"
        creative_payload = {
            'name': 'Sample promoted post',
            'object_story_spec': json.dumps({
                'page_id': PAGE_ID,
                'link_data': {
                    'message': adcreative.message,
                    'link': adcreative.link,
                    'image_hash': image_hash,
                    'call_to_action': {'type': "SHOP_NOW"}
                }
            }),
            'access_token': ACCESS_TOKEN
        }
        r3 = requests.post(creative_url, data=creative_payload).json()
        print(r3)
        adcreative.fb_creative_id = r3.get('id')
        adcreative.image_hash = image_hash
        adcreative.save()

        # 4. Create Ad
        ad_url = f"https://graph.facebook.com/v22.0/{AD_ACCOUNT_ID}/ads"
        ad_payload = {
            'name': 'My Ad',
            'adset_id': adset.fb_adset_id,
            'creative': json.dumps({'creative_id': adcreative.fb_creative_id}),
            'status': 'PAUSED',
            'access_token': ACCESS_TOKEN
        }
        r4 = requests.post(ad_url, data=ad_payload).json()
        print(r4)
        Ad.objects.create(
            campaign=campaign,
            name='My Ad',
            fb_ad_id=r4.get('id'),
            status='PAUSED'
        )
        campaign.status = 'Paused'
        campaign.save()
        return True

    except Exception as e:
        print(f"[ERROR] Facebook Ad Flow Failed: {e}")
        return False
