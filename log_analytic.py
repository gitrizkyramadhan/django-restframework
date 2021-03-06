from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
class AnalyticLog(object):
    
    def __init__(self):        

        self.client = MongoClient("mongodb://139.59.96.133:27017")
        self.db = self.client['bangjoni']
        print 'AnalyticLog added ...'

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

    def get_reminder_pulsa(self):
        
        query_get_reminder_today = [
            {"$match": {"type_reminder": "pulsa"}}
            ,
            {"$project": {"msisdn" : "$msisdn","type_reminder": "$type_reminder","date_execution": "$date_execution", "phone" : "$phone",
            "filter_date": { "$dateToString": { "format": "%Y%m%d", "date": "$date_execution" } },
            "value" : "$value"}
            }
            ,
            {"$match": {"type_reminder": "pulsa", "filter_date" :  datetime.now().strftime("%Y%m%d")}
            }
        ]
        
        return list(self.db.reminder.aggregate(query_get_reminder_today))

    def get_reminder_weather(self):
        # query_get_reminder_today = [
        #     {"$project": {"msisdn": "$msisdn", "type_reminder": "$type_reminder", "date_execution": "$date_execution",
        #                   "filter_date": {"$dateToString": {"format": "%Y%m%d", "date": "$date_execution"}},
        #                   "value": "$value"}
        #      }
        #     ,
        #     {"$match": {"type_reminder": "weather"}
        #      }
        # ]
        # return list(self.db.reminder.aggregate(query_get_reminder_today))
        return list(self.db.reminder.find({"type_reminder" : "weather"}))

    def get_often_location_access(self):

        query_get_often_location = [
            {"$group": {"_id": {"msisdn":"$msisdn", "location": "$location"}, "count": {"$sum": 1}}},
            {"$group": {"_id": {"msisdn": "$_id.msisdn", "location": "$_id.location"}, "count": {"$max": "$count"}}},
            {"$sort":  {"msisdn": -1}}
        ]

        return list(self.db.loglocation.aggregate(query_get_often_location))

    def get_max_batchid_track_reminder(self):

        query_get_max_batchid = [
                {"$group": {"_id": "1", "batchid": {"$max": "$batchid"}}}
        ]

        return list(self.db.track_reminder.aggregate(query_get_max_batchid))

    def get_msisdn_blast(self):

        # query_get_msisdn_blast = [
        #     {"desc": "blast"}, {"msisdn": "1"}
        #
        # ]

        return list(self.db.track_reminder.find({"desc": "blast"}, {"msisdn": "1"}))

    def get_new_converstion_word(self):

        query_get_error_answer = [
            #{"$match": {"incomingmsisdn": {"$regex" : "ngerti"}}}
            {"$match": {"$and" : [{"$or": [{"incomingmsisdn": {"$regex" : "ngerti"}},
                                {"incomingmsisdn": {"$regex" : "maaf"}},{"incomingmsisdn": {"$regex" : "err"}}]}
                                  ,{"question" : {"$regex" : "^((?!pulsa).)*$"}}
                                  ,{"question" : {"$regex" : "^((?!bjpay).)*$"}}
                                  ,{"question": {"$regex": "^((?!register).)*$"}}
                                  ,{"question": {"$regex": "^((?!ribu).)*$"}},
                                  {"question": {"$regex": "^((?!transfer).)*$"}},
                                  {"question": {"$regex": "^((?!halo bang).)*$"}},
                                  {"question": {"$regex": "^((?!permata).)*$"}},
                                  {"question": {"$regex": "^((?!kuota).)*$"}},
                                  {"question": {"$regex": "^((?!ref ).)*$"}},
                                  {"question": {"$ne": "ya"}},
                                  {"question": {"$ne": "gak"}},
                                  {"question": {"$ne": "ga"}},
                                  {"question": {"$ne": "nggak"}},
                                  {"question": {"$ne": "enggak"}},
                                  {"question": {"$ne": "iya"}},
                                  {"question": {"$ne": "get a friend"}},
                                  {"question": {"$ne": "inggris"}},
                                  {"question": {"$ne": "perancis"}}
                                  ]}},
            {"$group": {"_id": {"question" : "$question"}, "jmldata": {"$sum": 1}}},
            {"$match": {"jmldata": {"$gt": 3}}},
            {"$sort": {"jmldata": -1}}
        ]

        return list(self.db.conversation.aggregate(query_get_error_answer))

    def get_pulsa_data(self, msisdn, phone):

        if msisdn != '' and phone != '':
            return list(self.db.logpulsa.find({"msisdn" : msisdn, "phone" : phone}, {"msisdn": "msisdn", "denom": "denom",
                                                   "phone": "phone", "datetime": "datetime"})
                        .sort([("phone", ASCENDING), ("dateteime", ASCENDING)]))
        else :
            return list(self.db.logpulsa.find({}, {"msisdn": "msisdn", "denom": "denom","phone": "phone", "datetime": "datetime"})
                        .sort([("phone", ASCENDING), ("dateteime", ASCENDING)]).limit(10))

    def get_pulsa_recomend(self,msisdn):

        query_get_pulsa_recomend = [{"$match" : {"msisdn" : msisdn}},
        {"$group" : {"_id" : {"msisdn" : "$msisdn" , "phone" : "$phone"} , "count" : {"$sum" : 1}}},
        {"$sort" : {"msisdn" : 1 , "count" : -1}},
        {"$limit" : 3}
        ]

        return list(self.db.logpulsa.aggregate(query_get_pulsa_recomend))

    def get_count_flight(self):

        query = [{"$match": {"question" : {"$regex" : "pesawat"}}},
                  {"$project": {"datetime": "$datetime","convert_datetime": {"$dateToString": {"format": "%Y%m%d", "date": "$datetime"}},"value": "$value"}},
                 {"$group" : {"_id" : {"date" : "$convert_datetime"} , "count" : {"$sum" : 1}}},{"$sort" : {"_id" : -1}}
                 ]

        return list(self.db.conversation.aggregate(query))

    def get_count_freechat(self):
        query = [{"$match": {"topic": "tebak_tebakan"}},
                 {"$project": {"datetime": "$datetime",
                               "convert_datetime": {"$dateToString": {"format": "%Y%m%d", "date": "$datetime"}},
                               "value": "$value"}},
                 {"$group": {"_id": {"date": "$convert_datetime"}, "count": {"$sum": 1}}}, {"$sort": {"_id": -1}}
                 ]

        return list(self.db.conversation.aggregate(query))

    # def blast_pulsa_reminder_today

al = AnalyticLog()
print al.get_new_converstion_word()
