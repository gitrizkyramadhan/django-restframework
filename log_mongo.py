from datetime import datetime
from pymongo import MongoClient

class MongoLog(object):


    def __init__(self):
        print "Mongo has been loaded"
        self.client = MongoClient("mongodb://139.59.96.133:27017")
        self.db = self.client['bangjoni']


    def log_pulsa(self, msisdn, denom, phone):
        result = self.db.logpulsa.insert_one({
            "msisdn" : msisdn,
            "datetime" : datetime.now(),
            "denom" : denom,
            "phone" : phone
        })
        print ""


    def log_token(self, msisdn, denom, no_listrik, watt):
        result = self.db.logpln.insert_one({
            "msisdn" : msisdn,
            "datetime" : datetime.now(),
            "denom" : denom,
            "listrik" : no_listrik,
            "watt" : watt
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