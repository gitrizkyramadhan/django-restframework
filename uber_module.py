import json
from yaml import safe_dump
import pickle

import uber_utils
from example import utils
from example.utils import fail_print
from example.utils import response_print
from example.utils import success_print
from example.utils import import_app_credentials

from uber_rides.session import Session
from uber_rides.auth import AuthorizationCodeGrant
from uber_rides.client import UberRidesClient
from uber_rides.errors import ClientError
from uber_rides.errors import ServerError
from uber_rides.errors import UberIllegalState

from nlp_rivescript import Nlp


SERVER_TOKEN = 'azt8FFGw80YQtGHEEglfibFTR9GlGUmojXdtGfHD'
CLIENT_ID = 'EZx9ssXyrJFuWTqI_Unh_5guHIvAJyV9'
CLIENT_SECRET = 'KZRRW1yVSJJVNrKLRVsS9AT89VvuLoUDHYhHKFtI'
REDIRECT_URL = 'https://www.bangjoni.com/uber_token'

class UberService():

    def __init__(self):
        print "Uber module loaded"
        self.redis = Nlp().redisconn

    def get_products(self, origin, destination):
        session = Session(server_token=SERVER_TOKEN)
        client = UberRidesClient(session)
        response = client.get_products(origin['lat'], origin['lng'])
        products = response.json.get('products')
        print json.dumps(products)

        response = client.get_price_estimates(
            start_latitude=origin['lat'],
            start_longitude=origin['lng'],
            end_latitude=destination['lat'],
            end_longitude=destination['lng']
        )
        estimate = response.json.get('prices')
        print estimate
        print json.dumps(response.json)

    def get_auth(self, origin, destination):
        auth_flow = AuthorizationCodeGrant(CLIENT_ID,{'profile','request'},CLIENT_SECRET,REDIRECT_URL)
        auth_url = auth_flow.get_authorization_url()
        self.AUTH = auth_flow
        # print auth_url
        self.redis.set('ub/123', pickle.dumps(auth_flow))
        return auth_url
        # session = auth_flow.get_session(auth_url)
        # client = UberRidesClient(session, sandbox_mode=True)

    def get_client(self, state, code):
        # state = ti12Pnewi7FHXsEWC7OAz9gqlE85ais2 & code = ovNXkhAGr2oVSFDF7fAJJGCJGZDeAU
        # client = UberRidesClient(session)

        auth_flow = pickle.loads(self.redis.get('ub/123'))
        redirect_url = REDIRECT_URL + "?code="+str(code)+"&state="+str(state)
        # auth_flow = ClientCredentialGrant(CLIENT_ID, {'profile','request'}, CLIENT_SECRET)

        # auth_flow = self.AUTH
        # auth_flow.state_token = state
        # auth_flow = self.AUTH
        # auth_flow = AuthorizationCodeGrant(CLIENT_ID,{'profile','request'},CLIENT_SECRET,REDIRECT_URL, state)

        session = auth_flow.get_session(redirect_url)
        client = UberRidesClient(session, sandbox_mode=True)
        credentials = session.oauth2credential
        print credentials

        response = client.get_user_profile()
        profile = response.json

        first_name = profile.get('first_name')
        last_name = profile.get('last_name')
        email = profile.get('email')

ub = UberService()
ub.get_products({'lat':-6.2501281, 'lng':106.5996596}, {'lat':-6.2506642, 'lng':106.6244879})
print ub.get_auth('','')
# ub.get_client('ti12Pnewi7FHXsEWC7OAz9gqlE85ais2', 'ovNXkhAGr2oVSFDF7fAJJGCJGZDeAU')

# credentials = import_app_credentials(uber_utils.CREDENTIALS_FILENAME)
#
# api_client = ub.authorization_code_grant_flow(
#     credentials,
#     uber_utils.STORAGE_FILENAME,
#     'ti12Pnewi7FHXsEWC7OAz9gqlE85ais2',
#     'ovNXkhAGr2oVSFDF7fAJJGCJGZDeAU'
# )
#
# ub.hello_user(api_client)
