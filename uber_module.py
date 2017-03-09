import json
from uber_rides.session import Session
from uber_rides.client import UberRidesClient
from uber_rides.auth import AuthorizationCodeGrant


class UberService():

    def __init__(self):
        print "Uber module loaded"
        self.session = Session(server_token="EZx9ssXyrJFuWTqI_Unh_5guHIvAJyV9")
        self.client = UberRidesClient(self.session)

    def get_products(self, origin, destination):
        response = self.client.get_products(-6.2501281, 106.5996596)
        products = response.json.get('products')
        print json.dumps(products)

        response = self.client.get_price_estimates(
            start_latitude=-6.2501281,
            start_longitude=106.5996596,
            end_latitude=-6.2506642,
            end_longitude=106.6244879,
            seat_count=2
        )
        estimate = response.json.get('prices')
        print json.dumps(response.json)

ub = UberService()
ub.get_products({}, {})