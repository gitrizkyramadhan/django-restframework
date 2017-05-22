from datetime import datetime, timedelta
# import MySQLdb
import logging
from nlp_rivescript import Nlp
# from log_mongo import MongoLog
import requests
import json
import urllib

class FlightTiket():

    API = "https://api.tiket.com"
    SANDBOX_API = "http://api-sandbox.tiket.com"
    sandbox = False #True

    def __init__(self):
        with open('BJCONFIG.txt') as f:
            content = f.read().splitlines()
        f.close()

        self.MYSQL_HOST=content[12].split('=')[1]
        self.MYSQL_USER=content[13].split('=')[1]
        self.MYSQL_PWD=content[14].split('=')[1]
        self.MYSQL_DB=content[15].split('=')[1]

        print "Flight Tiket.com Module has been loaded"

    def add_order(self, msisdn, form_data, flight_data, **params):
        url_add_flight = self._get_url() + "/order/add/flight?"
        url_param = ''
        token = flight_data['request']['tiket_token']

        if params.get('roundtrip') == False:
            for form in form_data:
                if form['name'] == 'conFirstName':
                    firstName = urllib.quote_plus(form['value'])
                elif form['name'] == 'conPhone':
                    phone = urllib.quote_plus(form['value'])
                elif form['name'] == 'conEmailAddress':
                    emailAddress = urllib.quote_plus(form['value'])

                if form['name'] == 'conSalutation' :
                    if form['value'] == 'TUAN':
                        title = "Mr"
                    elif form['value'] == 'NYONYA':
                        title = "Mrs"
                    url_add_flight = url_add_flight + form['name'] + "=" + title + "&"
                    url_param = url_param + form['name'] + "=" + title + "&"
                    salutation = title
                else:
                    url_add_flight = url_add_flight + form['name'] + "=" + urllib.quote_plus(form['value']) + "&"
                    url_param = url_param + form['name'] + "=" + urllib.quote_plus(form['value']) + "&"
            departure_flight_id = flight_data['result']['departure']['id']
            # airline_name = flight_data['result']['departure']['original_result']['airlines_name']
            url_add_flight = url_add_flight + "token=" + token + "&flight_id=" + departure_flight_id + "&output=json"
            url_param = url_param + "token=" + token + "&flight_id=" + departure_flight_id + "&output=json"
            # print url_add_flight
            # print url_param
            return url_param
        else :
            departure_flight_id = flight_data['result']['departure']['departure']['id']
            ret_flight_id = flight_data['result']['return']['return']['id']

            for form in form_data:
                if form['name'] == 'conFirstName':
                    firstName = urllib.quote_plus(form['value'])
                elif form['name'] == 'conPhone':
                    phone = urllib.quote_plus(form['value'])
                elif form['name'] == 'conEmailAddress':
                    emailAddress = urllib.quote_plus(form['value'])

                if form['name'] == 'conSalutation':
                    if form['value'] == 'TUAN':
                        title = "Mr"
                    elif form['value'] == 'NYONYA':
                        title = "Mrs"
                    url_add_flight = url_add_flight + form['name'] + "=" + title + "&"
                    url_param = url_param + form['name'] + "=" + title + "&"
                    salutation = title
                else:
                    url_add_flight = url_add_flight + form['name'] + "=" + urllib.quote_plus(form['value']) + "&"
                    url_param = url_param + form['name'] + "=" + urllib.quote_plus(form['value']) + "&"

            url_param = url_param + "token=" + token + "&flight_id=" + departure_flight_id + "&ret_flight_id=" + ret_flight_id + "&output=json"
            # print url_add_flight
            # print url_param
            return url_param


    def get_url_payment(self, msisdn, order_id, type):
        token = '88f7fc398a2a6ef6590d441ef70e25764ab3174f'
        headers = {
            'User-Agent': 'twh:[21060440];[kenzie_tiket];'
        }
        # AVAILABLE PAYMENT
        url_checkout_customer = self._get_url() + '/checkout/checkout_payment?token=' + token + '&output=json'
        print url_checkout_customer
        r = requests.get(url_checkout_customer, headers=headers)
        print json.dumps(r.json())
        available_payments = json.loads(json.dumps(r.json()))
        if available_payments['diagnostic']['status'] != 200:
            raise Exception(available_payments['diagnostic']['error_msgs'])

        token = ''
        for available_pmt in available_payments['available_payment'] :
            if available_pmt['text'] == type:
                url_payment = available_pmt['link']

        return url_payment

    def pay_order(self, msisdn, order_id, url_payment):
        headers = {
            'User-Agent': 'twh:[21060440];[kenzie_tiket];'
        }
        token = ''
        url_payment = url_payment + "?btn_booking=1&currency=IDR&output=json&token=" + token
        print url_payment
        r = requests.get(url_payment, headers=headers)
        print json.dumps(r.json())
        payment = json.loads(json.dumps(r.json()))
        if payment['diagnostic']['status'] != 200:
            raise Exception(payment['diagnostic']['error_msgs'])


    def generate_params(self, token, form_data, flight_data, **params):

        print token, params

    def _get_url(self):
        if self.sandbox :
            return self.SANDBOX_API
        else :
            return self.API


# flight = FlightTiket()
# print flight.add_order('msisdn', [{"name":"conSalutation","value":"TUAN"},{"name":"conEmailAddress","value":"a2c6dfee7e69677cc7c9@cloudmailin.net"},{"name":"conFirstName","value":"batika"},{"name":"conPhone","value":"85790888409"},{"name":"titlea1","value":"TUAN"},{"name":"firstnamea1","value":"batika anda"}],
#                        {"result": {"departure": {"id": "239067466", "flight_number": "ID-7043",
#                                                  "full_via": "HLP - SOC (16:05 - 17:15)",
#                                                  "image": "https://cdn01.tiket.photos/images/flight/logo/icon_batik.png",
#                                                  "simple_departure_time": "16:05", "simple_arrival_time": "17:15",
#                                                  "transit": "Langsung", "origin": "HLP", "destination": "SOC",
#                                                  "duration": "1 j 10 m", "price": "407000.00",
#                                                  "original_result": {"flight_id": "239067466", "airlines_name": "BATIK",
#                                                                      "flight_number": "ID-7043",
#                                                                      "departure_city": "HLP", "arrival_city": "SOC",
#                                                                      "stop": "Langsung", "price_value": "407000.00",
#                                                                      "price_adult": "407000.00", "price_child": "0.00",
#                                                                      "price_infant": "0.00",
#                                                                      "timestamp": "2017-04-26 22:20:14",
#                                                                      "has_food": "1", "check_in_baggage": "20",
#                                                                      "is_promo": 1, "airport_tax": '',
#                                                                      "check_in_baggage_unit": "Kg",
#                                                                      "simple_departure_time": "16:05",
#                                                                      "simple_arrival_time": "17:15", "long_via": "",
#                                                                      "departure_city_name": "Jakarta Halim",
#                                                                      "arrival_city_name": "Solo",
#                                                                      "full_via": "HLP - SOC (16:05 - 17:15)",
#                                                                      "markup_price_string": "", "need_baggage": 0,
#                                                                      "best_deal": '', "duration": "1 j 10 m",
#                                                                      "image": "https://cdn01.tiket.photos/images/flight/logo/icon_batik.png",
#                                                                      "departure_flight_date": "2017-05-02 16:05:00",
#                                                                      "departure_flight_date_str": "Selasa, 02 Mei 2017",
#                                                                      "departure_flight_date_str_short": "Sel, 02 Mei 2017",
#                                                                      "arrival_flight_date": "2017-05-02 17:15:00",
#                                                                      "arrival_flight_date_str": "Selasa, 02 Mei 2017",
#                                                                      "arrival_flight_date_str_short": "Sel, 02 Mei 2017",
#                                                                      "flight_infos": {"flight_info": [
#                                                                          {"flight_number": "ID-7043", "class": "Promo",
#                                                                           "departure_city": "HLP",
#                                                                           "departure_city_name": "Jakarta Halim",
#                                                                           "arrival_city": "SOC",
#                                                                           "arrival_city_name": "Solo",
#                                                                           "airlines_name": "BATIK",
#                                                                           "departure_date_time": "2017-05-02 16:05:00",
#                                                                           "string_departure_date": "Selasa, 02 Mei 2017",
#                                                                           "string_departure_date_short": "Sel, 02 Mei 2017",
#                                                                           "simple_departure_time": "16:05",
#                                                                           "arrival_date_time": "2017-05-02 17:15:00",
#                                                                           "string_arrival_date": "Selasa, 02 Mei 2017",
#                                                                           "string_arrival_date_short": "Sel, 02 Mei 2017",
#                                                                           "simple_arrival_time": "17:15",
#                                                                           "img_src": "https://cdn01.tiket.photos/images/flight/logo/icon_batik.png",
#                                                                           "duration_time": 4200, "duration_hour": "1j",
#                                                                           "duration_minute": "10m",
#                                                                           "check_in_baggage": 20,
#                                                                           "check_in_baggage_unit": "Kg", "terminal": "",
#                                                                           "transit_duration_hour": 0,
#                                                                           "transit_duration_minute": 0,
#                                                                           "transit_arrival_text_city": "",
#                                                                           "transit_arrival_text_time": ""}]},
#                                                                      "sss_key": ''}}, "total_price": 407000,
#                                    "type": "tiket", "destination_name": "Adisumarmo",
#                                    "origin_name": "Halim Perdanakusuma", "departure_date_formatted": "02 Mei 2017",
#                                    "msisdn": "abc"},
#                         "request": {"origin": "HLP", "destination": "SOC", "adult": "1", "child": "0", "infant": "0",
#                                     "departure_date": "2017-05-02", "airline": "", "flight_time": "", "transit": 0,
#                                     "tiket_token": "b1d5bb73a03943b75d3220f25df0a9687d545d1c", "msisdn": "abc"}})
# print flight.get_url_payment('msisdn', 'order_id', 'ATM Transfer')