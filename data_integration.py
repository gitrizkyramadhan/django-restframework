from pymongo import MongoClient
from log_analytic import AnalyticLog
from log_mongo import MongoLog
from parse_log import UnstructureLog, StructuredLog
from datetime import datetime, timedelta, time
class DataIntegration(object):
    
    def __init__(self):        

        self.client = MongoClient("mongodb://localhost:27017")
        self.db = self.client['bangjoni']
        print 'DataIntegration addded ...'

    def job_logpulsa_to_reminder(self):
        
        al = AnalyticLog()
        ml = MongoLog()
        for data in al.get_max_pulsa() :
            # print str(data['datetime']) + ' ' + str(datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S') + timedelta(days = 30))
            
            self.db.reminder.delete_one({ "msisdn" : data['msisdn'] }) #delete msisdn first
            ml.reminder(data['msisdn'], "pulsa", data['denom'], 
            datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S') + timedelta(days = 30)) # fill reminder collection
    
    def job_celerylog_to_locationlog(self):
        
        ml = MongoLog()
        ul = UnstructureLog()
        for data in ul.parse_celery_log('celery1__20170205_12.log'):
            ml.log_location(data[0], data[1][0], data[1][1])
    
    def job_migrate_log_pulsa(self):

        ml = MongoLog()
        sl = StructuredLog()
        data_log = sl.parse_log('F_BJPTRX.log')
        for data in data_log:
            ml.log_pulsa_migrate(data[1], data[3], data[5], data[2])
        

    def job_loglocation_to_reminder(self):

        ml = MongoLog()
        la = AnalyticLog()
        for data in la.get_often_location_access():

            ml.reminder(data['_id'], 'location', data[''], data[2])