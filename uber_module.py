import json
import pickle

from uber_rides.auth import AuthorizationCodeGrant
from uber_rides.auth import OAuth2Credential
from uber_rides.client import UberRidesClient, SurgeError
from uber_rides.session import Session

from nlp_rivescript import Nlp

SERVER_TOKEN = 'azt8FFGw80YQtGHEEglfibFTR9GlGUmojXdtGfHD'
CLIENT_ID = 'EZx9ssXyrJFuWTqI_Unh_5guHIvAJyV9'
CLIENT_SECRET = 'KZRRW1yVSJJVNrKLRVsS9AT89VvuLoUDHYhHKFtI'
REDIRECT_URL = 'https://www.bangjoni.com/uber_token'
SCOPES = {'profile','request'}
SANDBOX_MODE = True
PRODUCT_FILTER = "89da0988-cb4f-4c85-b84f-aac2f5115068,776ea734-1404-4a40-bf09-ebcb2acf6f2b"

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
        return UberRidesClient(session, sandbox_mode=SANDBOX_MODE)


    def get_products(self, origin, destination, filters=""):
        session = Session(server_token=SERVER_TOKEN)
        client = UberRidesClient(session, sandbox_mode=SANDBOX_MODE)
        response = client.get_products(origin['lat'], origin['lng'])
        products = response.json.get('products')
        # print json.dumps(products)

        response = client.get_price_estimates(
            start_latitude=origin['lat'],
            start_longitude=origin['lng'],
            end_latitude=destination['lat'],
            end_longitude=destination['lng']
        )
        estimates = response.json.get('prices')

        filtered_products = []
        for estimate in estimates :
            for filter_str in filters.split(",") :
                if estimate['product_id'] == filter_str :
                    formatted_amt = 'Rp '+str('{:,.0f}'.format(int(estimate['low_estimate'])))+' - Rp '+str('{:,.0f}'.format(int(estimate['high_estimate'])))
                    estimate['formatted_amt'] = formatted_amt
                    filtered_products.append(estimate)

        return filtered_products


    def get_auth(self, msisdn):
        auth_flow = AuthorizationCodeGrant(CLIENT_ID,SCOPES,CLIENT_SECRET,REDIRECT_URL)
        auth_url = auth_flow.get_authorization_url()
        self.state_uber = auth_flow.state_token
        # print auth_url
        incomingMsisdn = json.loads(self.redis.get("inc/%s" % (msisdn)))
        incomingMsisdn[1] = pickle.dumps(auth_flow)
        self.redis.set("inc/%s" % (msisdn), json.dumps(incomingMsisdn))
        return auth_flow
        # session = auth_flow.get_session(auth_url)
        # client = UberRidesClient(session, sandbox_mode=True)

    def create_client(self, msisdn, state, code):
        # state = ti12Pnewi7FHXsEWC7OAz9gqlE85ais2 & code = ovNXkhAGr2oVSFDF7fAJJGCJGZDeAU
        # client = UberRidesClient(session)

        # auth_flow = pickle.loads(self.redis.get('ub/123'))
        incomingMsisdn = json.loads(self.redis.get("inc/%s" % (msisdn)))
        auth_flow = pickle.loads(incomingMsisdn[1])
        # self.redis.set("inc/%s" % (msisdn), json.dumps(incomingMsisdn))
        # redirect_url = REDIRECT_URL + "?code="+str(code)+"&state="+str(self.state_uber)
        redirect_url = REDIRECT_URL + "?code="+str(code)+"&state="+str(state)
        # auth_flow = ClientCredentialGrant(CLIENT_ID, {'profile','request'}, CLIENT_SECRET)

        # auth_flow = self.AUTH
        # auth_flow.state_token = state
        # auth_flow = self.AUTH
        # auth_flow = AuthorizationCodeGrant(CLIENT_ID,{'profile','request'},CLIENT_SECRET,REDIRECT_URL, state)

        session = auth_flow.get_session(redirect_url)
        client = UberRidesClient(session, sandbox_mode=SANDBOX_MODE)
        credentials = session.oauth2credential
        self.redis.set("cred/%s" % (msisdn), pickle.dumps(credentials))
        # print credentials

        response = client.get_user_profile()
        profile = response.json

        first_name = profile.get('first_name')
        last_name = profile.get('last_name')
        email = profile.get('email')

        return (first_name, last_name, email)


    def estimate_price(self, msisdn, credential, origin, destination):
        # credential = pickle.loads(self.redis.get('cred/123'))
        client = self.create_uber_client(credential.access_token,credential.expires_in_seconds, credential.grant_type, credential.refresh_token)
        estimate = client.estimate_ride(
            product_id='89da0988-cb4f-4c85-b84f-aac2f5115068',
            start_latitude=origin['lat'],
            start_longitude=origin['lng'],
            end_latitude=destination['lat'],
            end_longitude=destination['lng']
        )
        fare = estimate.json.get('fare')
        print json.dumps(estimate.json.get('fare'))
        # request = client.request_ride(
        #     product_id='89da0988-cb4f-4c85-b84f-aac2f5115068',
        #     start_latitude=origin['lat'],
        #     start_longitude=origin['lng'],
        #     end_latitude=destination['lat'],
        #     end_longitude=destination['lng'],
        #     seat_count=1,
        #     fare_id=fare['fare_id']
        # )
        # print json.dumps(request.json)


    def check_surge(self, msisdn, credential, product_id):
        # cred = pickle.loads(self.redis.get('cred/123'))
        client = self.create_uber_client(credential.access_token, credential.expires_in_seconds, credential.grant_type, credential.refresh_token)
        # result = client.get_product(product_id)
        result = client.update_sandbox_product('89da0988-cb4f-4c85-b84f-aac2f5115068', 1.0, True)
        print json.dumps(result.json)


    def get_payment_methods(self, msisdn, credential):
        # cred = pickle.loads(self.redis.get('cred/123'))
        client = self.create_uber_client(credential.access_token, credential.expires_in_seconds, credential.grant_type, credential.refresh_token)
        result = client.get_payment_methods()
        print json.dumps(result.json)


    def request_ride(self, msisdn, credential, origin, destination, product_id, fare_id, surge_id=None):
        # cred = pickle.loads(self.redis.get('cred/123'))
        client = self.create_uber_client(credential.access_token, credential.expires_in_seconds, credential.grant_type, credential.refresh_token)
        estimate = client.estimate_ride(
            product_id=product_id,
            start_latitude=origin['lat'],
            start_longitude=origin['lng'],
            end_latitude=destination['lat'],
            end_longitude=destination['lng']
        )
        fare = estimate.json.get('fare')
        print json.dumps(estimate.json.get('fare'))
        request = client.request_ride(
            product_id=product_id,
            start_latitude=origin['lat'],
            start_longitude=origin['lng'],
            end_latitude=destination['lat'],
            end_longitude=destination['lng'],
            seat_count=1,
            fare_id=fare['fare_id'],
            surge_confirmation_id=surge_id
        )
        print json.dumps(request.json)
        return request.json
        # except SurgeError as ce :
            # client.
            # print ce.surge_confirmation_href
            # print ce.surge_confirmation_id


    def get_ride_detail(self, msisdn, credential, ride_id):
        client = self.create_uber_client(credential.access_token, credential.expires_in_seconds, credential.grant_type,
                                         credential.refresh_token)
        ride_details = client.get_ride_details(ride_id)
        return ride_details.json


    def cancel_current_ride(self, msisdn, credential):
        # cred = pickle.loads(self.redis.get('cred/123'))
        client = self.create_uber_client(credential.access_token, credential.expires_in_seconds, credential.grant_type, credential.refresh_token)
        result = client.cancel_current_ride()
        print json.dumps(result.json)

    def update_ride(self, msisdn, credential, request_id, status):
        client = self.create_uber_client(credential.access_token, credential.expires_in_seconds, credential.grant_type,
                                         credential.refresh_token)
        update_product = client.update_sandbox_ride(request_id, status)
        print update_product



ub = UberService()
# print json.dumps(ub.get_products({'lat':-6.2501281, 'lng':106.5996596}, {'lat':-6.2506642, 'lng':106.6244879}, PRODUCT_FILTER))
# print ub.get_auth('','')

# redirect_url = 'Copy the URL you are redirected to and paste here: \n'
# print ub.get_client('ymrvKm8qNFvrsJWBQv7Fx1XmBKW2rfQf', 'rVrz5IFkYHXQLlWne0cFFmbdscHCqY')

# ub.estimate_price('abc', pickle.loads(ub.redis.get('cred/123')), {'lat':-6.2501281, 'lng':106.5996596}, {'lat':-6.1974559, 'lng':106.6244879})
# ub.get_payment_methods('msisdn', pickle.loads(ub.redis.get('cred/123')))

# ub.check_surge('msisdn', pickle.loads(ub.redis.get('cred/123')), '')
# ub.estimate_price('abc', pickle.loads(ub.redis.get('cred/123')), {'lat':-6.2501281, 'lng':106.5996596}, {'lat':-6.1974559, 'lng':106.6244879})
# ub.request_ride('', pickle.loads(ub.redis.get('cred/123')), {'lat':-6.2501281, 'lng':106.5996596}, {'lat':-6.1974559, 'lng':106.6244879}, '89da0988-cb4f-4c85-b84f-aac2f5115068', 'f5fc1593dc398afa7ab9207ba984f1896a1e3a80a497a27b0283c162922ba662')
# ub.update_ride('msisdn', pickle.loads(ub.redis.get('cred/123')), "eb788779-dcf2-496a-b77f-9a6fb1e9dc06", 'accepted')

# print json.dumps(ub.get_ride_detail('msisdn', pickle.loads(ub.redis.get('cred/123')), 'eb788779-dcf2-496a-b77f-9a6fb1e9dc06'))

# ub.cancel_current_ride('mssidn', pickle.loads(ub.redis.get('cred/123')))
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
