from datetime import datetime
from pymongo import MongoClient

class MongoLog(object):


    def __init__(self):
        print "Mongo has been loaded"
        self.client = MongoClient("mongodb://139.59.96.133:27017")
        self.db = self.client['bangjoni']

    def log_service(self, msisdn, service_name):
        result = self.db.logservice.insert_one({
            "msisdn": msisdn,
            "datetime": datetime.now(),
            "service_name": service_name
        })

    def log_pulsa(self, msisdn, denom, phone):
        result = self.db.logpulsa.insert_one({
            "msisdn" : msisdn,
            "datetime" : datetime.now(),
            "denom" : denom,
            "phone" : phone
        })


    def log_token(self, msisdn, denom, no_listrik, watt):
        result = self.db.logpln.insert_one({
            "msisdn" : msisdn,
            "datetime" : datetime.now(),
            "denom" : denom,
            "listrik" : no_listrik,
            "watt" : watt
        })

    def log_zomato(self, msisdn, latitude, longitude, cuisine):
        result = self.db.logzomato.insert_one({
            "msisdn": msisdn,
            "datetime": datetime.now(),
            "latitude": latitude,
            "longitude": longitude,
            "cuisine": cuisine
        })

    def log_conversation(self, msisdn, question, answer, service, topic, incoming_msisdn):
        result = self.db.conversation.insert_one({
            "msisdn" : msisdn,
            "datetime" : datetime.now(),
            "question" : question,
            "answer" : answer,
            "service" : service,
            "topic" : topic,
            "incomingmsisdn" : incoming_msisdn
        })

    def log_debit(self, msisdn, phone, amount, transaction_id, description):
        result = self.db.bjpay_transactions.insert_one({
            "msisdn": msisdn,
            "datetime": datetime.now(),
            "phone": phone,
            "amount": amount,
            "transaction_id": transaction_id,
            "description": description,
            "type": "DEBIT"
        })

    def log_credit(self, msisdn, phone, amount, transaction_id, description):
        result = self.db.bjpay_transactions.insert_one({
            "msisdn": msisdn,
            "datetime": datetime.now(),
            "phone": phone,
            "amount": amount,
            "transaction_id": transaction_id,
            "description": description,
            "type": "CREDIT"
        })

    def log_bjpay_register(self, msisdn, phone, va_number):
        result = self.db.bjpay_register.insert_one({
            "msisdn": msisdn,
            "datetime": datetime.now(),
            "phone": phone,
            "va_number": va_number
        })

    def log_pulsa_migrate(self, msisdn, denom, date, phone):
        result = self.db.logpulsa.insert_one({
            "msisdn" : msisdn,
            "datetime" : date,
            "denom" : denom,
            "phone" : phone
        })

    def reminder(self, msisdn, type_reminder, value, date_execution):
        result = self.db.reminder.insert_one({
            "data_date" : datetime.now(),
            "msisdn" : msisdn,
            "type_reminder" : type_reminder,
            "value" : value,
            "date_execution" : date_execution
        })

    def log_location(self, msisdn, location, date_location):
        result = self.db.loglocation.insert_one({
            "data_date" : datetime.now(),
            "msisdn" : msisdn,
            "location" : location,
            "date_location" : date_location
        })

    def reminder_pulsa(self, msisdn, type_reminder, value, date_execution, phone):
        result = self.db.reminder.insert_one({
            "data_date" : datetime.now(),
            "msisdn" : msisdn,
            "type_reminder" : type_reminder,
            "value" : value,
            "date_execution" : date_execution,
            "phone" : phone
        })

    def log_track_reminder(self, batchid, msisdn, type_reminder, event_desc):
        result = self.db.track_reminder.insert_one({
            "data_date" : datetime.now(),
            "batchid" : batchid,
            "msisdn" : msisdn,
            "type_reminder" : type_reminder,
            "desc" : event_desc,
        })

    def log_ads(self, msisdn, adscode):
        result = self.db.logads.insert_one({
            "data_date" : datetime.now(),
            "msisdn" : msisdn,
            "adscode" : adscode
        })

# ml = MongoLog()
# ml.log_pulsa_migrate("U3b8faff6e0264b4d6e1dedf430d7ecf8", 5000, "2017-03-31 20:16:48", "083829570148")