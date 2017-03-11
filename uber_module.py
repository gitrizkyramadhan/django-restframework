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
from uber_rides.auth import OAuth2Credential
from uber_rides.client import UberRidesClient
from uber_rides.errors import ClientError
from uber_rides.errors import ServerError
from uber_rides.errors import UberIllegalState

from nlp_rivescript import Nlp


SERVER_TOKEN = 'azt8FFGw80YQtGHEEglfibFTR9GlGUmojXdtGfHD'
CLIENT_ID = 'EZx9ssXyrJFuWTqI_Unh_5guHIvAJyV9'
CLIENT_SECRET = 'KZRRW1yVSJJVNrKLRVsS9AT89VvuLoUDHYhHKFtI'
REDIRECT_URL = 'https://www.bangjoni.com/uber_token'
SCOPES = {'profile','request'}

class UberService():

    def __init__(self):
        print "Uber module loaded"
        self.redis = Nlp().redisconn

    def create_uber_client(self, access_token, expires_in_seconds, grant_type, refresh_token):
        """Create an UberRidesClient from OAuth 2.0 credentials.
        Parameters
            credentials (dict)
                Dictionary of OAuth 2.0 credentials.
        Returns
            (UberRidesClient)
                An authorized UberRidesClient to access API resources.
        """
        oauth2credential = OAuth2Credential(
            client_id=CLIENT_ID,
            access_token=access_token,
            expires_in_seconds=expires_in_seconds,
            scopes=SCOPES,
            grant_type=grant_type,
            redirect_url=REDIRECT_URL,
            client_secret=CLIENT_SECRET,
            refresh_token=refresh_token,
        )
        session = Session(oauth2credential=oauth2credential)
        return UberRidesClient(session, sandbox_mode=True)

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
        auth_flow = AuthorizationCodeGrant(CLIENT_ID,SCOPES,CLIENT_SECRET,REDIRECT_URL)
        auth_url = auth_flow.get_authorization_url()
        self.state_uber = auth_flow.state_token
        # print auth_url
        self.redis.set('ub/123', pickle.dumps(auth_flow))
        return auth_url
        # session = auth_flow.get_session(auth_url)
        # client = UberRidesClient(session, sandbox_mode=True)

    def get_client(self, state, code):
        # state = ti12Pnewi7FHXsEWC7OAz9gqlE85ais2 & code = ovNXkhAGr2oVSFDF7fAJJGCJGZDeAU
        # client = UberRidesClient(session)

        auth_flow = pickle.loads(self.redis.get('ub/123'))
        # redirect_url = REDIRECT_URL + "?code="+str(code)+"&state="+str(self.state_uber)
        redirect_url = REDIRECT_URL + "?code="+str(code)+"&state="+str(state)
        # auth_flow = ClientCredentialGrant(CLIENT_ID, {'profile','request'}, CLIENT_SECRET)

        # auth_flow = self.AUTH
        # auth_flow.state_token = state
        # auth_flow = self.AUTH
        # auth_flow = AuthorizationCodeGrant(CLIENT_ID,{'profile','request'},CLIENT_SECRET,REDIRECT_URL, state)

        session = auth_flow.get_session(redirect_url)
        client = UberRidesClient(session, sandbox_mode=True)
        credentials = session.oauth2credential
        self.redis.set('cred/123', pickle.dumps(credentials))
        # print credentials

        response = client.get_user_profile()
        profile = response.json

        first_name = profile.get('first_name')
        last_name = profile.get('last_name')
        email = profile.get('email')

        return (first_name, last_name, email)


    def estimate_price(self, msisdn, origin, destination):
        cred = pickle.loads(self.redis.get('cred/123'))
        client = self.create_uber_client(cred.access_token,cred.expires_in_seconds, cred.grant_type, cred.refresh_token)
        estimate = client.estimate_ride(
            product_id='89da0988-cb4f-4c85-b84f-aac2f5115068',
            start_latitude=origin['lat'],
            start_longitude=origin['lng'],
            end_latitude=destination['lat'],
            end_longitude=destination['lng']
        )
        fare = estimate.json.get('fare')
        print json.dumps(estimate.json)
        request = client.request_ride(
            product_id='89da0988-cb4f-4c85-b84f-aac2f5115068',
            start_latitude=origin['lat'],
            start_longitude=origin['lng'],
            end_latitude=destination['lat'],
            end_longitude=destination['lng'],
            seat_count=1,
            fare_id=fare['fare_id']
        )
        print json.dumps(request.json)

    def cancel_current_ride(self, msisdn):
        cred = pickle.loads(self.redis.get('cred/123'))
        client = self.create_uber_client(cred.access_token, cred.expires_in_seconds, cred.grant_type, cred.refresh_token)
        client.cancel_current_ride()



ub = UberService()
# ub.get_products({'lat':-6.2501281, 'lng':106.5996596}, {'lat':-6.2506642, 'lng':106.6244879})
# print ub.get_auth('','')

# redirect_url = 'Copy the URL you are redirected to and paste here: \n'
# print ub.get_client('gwKtikZKGMkSOmiNekZhdvIHUrvk9qwO', 'A9F152N8n7Z8vgPn8YzFPr1cdzmF0i')

# ub.estimate_price('abc', {'lat':-6.2501281, 'lng':106.5996596}, {'lat':-6.1974559, 'lng':106.6244879})
ub.cancel_current_ride('')
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
