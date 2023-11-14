from decouple import config
from pipedrive.client import Client

client = Client(domain=config('PIPEDRIVE_DOMAIN'))
client.set_api_token(config('PIPEDRIVE_API_TOKEN'))
"""
response = client.deals.get_all_deals_with_filter(2)['data']
response2=client.deals.get_deal_products(43)['data']
#response=client.filters.get_all_filters()['data']
#for f in response:
    #print(f['name'],f['id'])
print(response[1])
print(response2)
print(len(response2))
"""

params = {
    'since_timestamp': '2023-11-09 00:00:00'
}
response = client.recents.get_recent_changes(params=params)['data']
print(len(response))
recently_edited_deals=[r for r in response if r['item']=='deal']
print(len(recently_edited_deals))
print([r['data']['title'] for r in recently_edited_deals])