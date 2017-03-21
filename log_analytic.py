from pymongo import MongoClient
from datetime import datetime
class AnalyticLog(object):
    
    def __init__(self):        

        self.client = MongoClient("mongodb://139.59.96.133:27017")
        self.db = self.client['bangjoni']
        print 'AnalyticLog addded ...'
    
    def get_max_pulsa(self):
        result = []
        query_max_date = [
            {"$group" : {"_id": {"msisdn": "$msisdn", "phone": "$phone"}, "max_date" : {"$max" : "$datetime"}}}
        ]
        for data in list(self.db.logpulsa.aggregate(query_max_date)):
            data_all = self.db.logpulsa.find_one({ "msisdn": data['_id']['msisdn'], 
            "phone": data['_id']['phone'], "datetime": data['max_date']})
            result.append(data_all)

        return result

    def get_reminder(self, type_reminder):
        
        query_get_reminder_today = [
            {"$project": {"msisdn" : "$msisdn","type_reminder": "$type_reminder","date_execution": "$date_execution",
            "filter_date": { "$dateToString": { "format": "%Y%m%d", "date": "$date_execution" } },
            "value" : "$value"}
            }
            ,
            {"$match": {"type_reminder": type_reminder,"filter_date" :  "20170322"} 
            }
            #datetime.now().strftime("%Y%m%d")
        ]
        
        return list(self.db.reminder.aggregate(query_get_reminder_today))

    def get_often_location_access(self):
        
        query_get_count = [
            {"$group" : {"_id": {"msisdn" :"$msisdn", "location" : "$location"}, "count" : {"$sum" : 1}}}   
        ]
        query_get_often_location = [
            {"$group" : {"_id": {"msisdn" :"$msisdn", "location" : "$location"}, "count" : {"$sum" : 1}}},
            {"$group" : {"_id": {"msisdn" : "$_id.msisdn"} , "count" : {"$max" : "$count"}}}
        ]

        for data in list(self.db.loglocation.aggregate(query_get_count)):
            for data_fiter in list(self.db.loglocation.aggregate(query_get_count)):
                data['_id']['msisdn'] == data_fiter

        return list(self.db.loglocation.aggregate(query_get_often_location))

