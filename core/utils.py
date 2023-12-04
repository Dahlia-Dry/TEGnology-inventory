from core.models import *
from decouple import config
from pipedrive.client import Client

def sync_pipedrive_latest():
    client = Client(domain=config('PIPEDRIVE_DOMAIN'))
    client.set_api_token(config('PIPEDRIVE_API_TOKEN'))
    t = Timestamp.objects.get(label='last_pipedrive_sync')
    params = {
    'since_timestamp': t.last_updated.strftime('%Y-%m-%d %H:%M:00'),
    }
    response = client.recents.get_recent_changes(params=params)
    if response['data'] is not None:
        new_deals = [item['data'] for item in response['data'] if item['item']=='deal' and item['data']['status']=='won']
        for d in new_deals:
            #print(d)
            org = client.organizations.get_organization(d['org_id'])['data']
            person = client.persons.get_person(d['person_id'])['data']
            customer_name = org['name']
            try:
                person = person['name']
            except:
                person=None
            try:
                email = person['email'][0]['value']
            except:
                email=None
            try:
                customer_instance=Customer.objects.get(name=customer_name)
            except:
                customer_instance= Customer.objects.create(name=customer_name,
                                        address=org['address']
                                        )
            customer_instance.save()
            try:
                o=Order.objects.get(pipedrive_id=d['id'])
            except:
                print(f"creating order record for {d['title']}")
                o = Order.objects.create(name=d['title'],
                                    pipedrive_id=d['id'],
                                    status_date=datetime.datetime.strptime(d['update_time'],'%Y-%m-%d %H:%M:%S').date(),
                                    close_date = datetime.datetime.strptime(d['close_time'],'%Y-%m-%d %H:%M:%S').date(),
                                    pipedrive_meta=d,
                                    total=d['weighted_value'],
                                    currency=d['formatted_value'][0],
                                    customer=customer_instance,
                                    contact_person=person,
                                    contact_email=email)
            else:
                print(f"updating order record for {d['title']}")
                o.status_date = datetime.datetime.strptime(d['update_time'],'%Y-%m-%d %H:%M:%S').date()
                o.close_date = datetime.datetime.strptime(d['close_time'],'%Y-%m-%d %H:%M:%S').date()
                o.pipedrive_meta=d
                o.total = d['weighted_value']
                o.currency = d['formatted_value'][0]
                o.customer=customer_instance
                o.contact_person=person
                o.contact_email=email
            print('saving order')
            o.save()
    t.save()

def fetch_emails(setting):
    if setting == 'notify_new_entry':
        pass
    elif setting == 'notify_new_order':
        pass
