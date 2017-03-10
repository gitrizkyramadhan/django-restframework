import json
from uber_rides.session import Session
from uber_rides.client import UberRidesClient
from uber_rides.auth import AuthorizationCodeGrant


class UberService():

    def __init__(self):
        print "Uber module loaded"
        self.session = Session(server_token="23nuN6asAXNFCn1uaDkCPN1ZVfdnQvdi_pJbF0L3")
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

ub = UberService()
ub.get_products({'lat':-6.2501281, 'lng':106.5996596}, {'lat':-6.2506642, 'lng':106.6244879})