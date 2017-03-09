import json
from uber_rides.session import Session
from uber_rides.client import UberRidesClient
from uber_rides.auth import AuthorizationCodeGrant


SERVER_TOKEN = 'azt8FFGw80YQtGHEEglfibFTR9GlGUmojXdtGfHD'
CLIENT_ID = 'EZx9ssXyrJFuWTqI_Unh_5guHIvAJyV9'
CLIENT_SECRET = 'KZRRW1yVSJJVNrKLRVsS9AT89VvuLoUDHYhHKFtI'
REDIRECT_URL = 'https://www.bangjoni.com/uber_token'

class UberService():

    def __init__(self):
        print "Uber module loaded"
        self.session = Session(server_token=SERVER_TOKEN)
        self.client = UberRidesClient(self.session)

    def get_products(self, origin, destination):
        response = self.client.get_products(origin['lat'], origin['lng'])
        products = response.json.get('products')
        print json.dumps(products)

        response = self.client.get_price_estimates(
            start_latitude=origin['lat'],
            start_longitude=origin['lng'],
            end_latitude=destination['lat'],
            end_longitude=destination['lng']
        )
        estimate = response.json.get('prices')
        print json.dumps(response.json)

    def authorize(self, origin, destination):
        auth_flow = AuthorizationCodeGrant(CLIENT_ID,{'profile','request'},CLIENT_SECRET,REDIRECT_URL)
        auth_url = auth_flow.get_authorization_url()
        print auth_url
        # session = auth_flow.get_session(auth_url)
        # client = UberRidesClient(session, sandbox_mode=True)
        # credentials = session.oauth2credential

ub = UberService()
ub.get_products({'lat':-6.2501281, 'lng':106.5996596}, {'lat':-6.2506642, 'lng':106.6244879})
ub.authorize('','')