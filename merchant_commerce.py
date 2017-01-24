from datetime import datetime, timedelta
from decimal import Decimal
from random import randint
import re

import requests
import json
import uuid

from dbutils import DBUtil

class MerchantCommerce:

    def __init__(self):
        print "Merchant Commerce class loaded"

        with open('BJCONFIG.txt') as f:
            content = f.read().splitlines()
        f.close()

        self.BASE_URL = content[10].split('=')[1]

    def createOrder(self, msisdn, userId, name, address, contact, lat, lng, **kwargs):
        print "creating order"
        data = {
            'customer' : {
                'name' : name,
                'address' : address,
                'contact' : contact,
                'custid' : msisdn
            },
            'order' : {
                'lat' : lat,
                'lng' : lng,
                'notes' : kwargs.get('notes', ''),
                'detail' : kwargs.get('detail', '')
            }
        }
        r = requests.post(self.BASE_URL+"order.php", data=json.dumps(data))
        decodedJson = json.dumps(r.json())
        decodedJson = json.loads(decodedJson)
        return decodedJson