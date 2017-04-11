from pymongo import MongoClient
from log_analytic import AnalyticLog
from log_mongo import MongoLog
from parse_log import UnstructureLog, StructuredLog
from datetime import datetime, timedelta, time
import MySQLdb
import numpy
import math
class DataIntegration(object):
    
    def __init__(self):        

        self.client = MongoClient("mongodb://139.59.96.133:27017")
        self.db = self.client['bangjoni']
        with open('BJCONFIG.txt') as f:
            content = f.read().splitlines()
        f.close()
        # TOKEN_TELEGRAM = content[0].split('=')[1]
        # KEYFILE = content[1].split('=')[1]
        # CERTFILE = content[2].split('=')[1]
        # URL_TELEGRAM = content[3].split('=')[1]
        self.MYSQL_HOST = content[4].split('=')[1]
        self.MYSQL_USER = content[5].split('=')[1]
        self.MYSQL_PWD = content[6].split('=')[1]
        self.MYSQL_DB = content[7].split('=')[1]
        # WEB_HOOK = content[8].split('=')[1]
        # EMAIL_NOTIF = content[9].split('=')[1]
        # LINE_TOKEN = content[11].split('=')[1]
        print 'DataIntegration added ...'

    def request(self, sql):
        # print self.MYSQL_HOST, self.MYSQL_DB, self.MYSQL_USER, self.MYSQL_PWD
        try:
            db_connect = MySQLdb.connect(host=self.MYSQL_HOST, port=3306, user=self.MYSQL_USER, passwd=self.MYSQL_PWD, db=self.MYSQL_DB)
            # Create cursor
            cursor = db_connect.cursor()
            cursor.execute(sql)
            sqlout = cursor.fetchall()
            return sqlout
        except MySQLdb.Error, e:
            logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            print e.args
            print "ERROR: %d: %s" % (e.args[0], e.args[1])

    def insert(self , sql):
        try:
            db_connect = MySQLdb.connect(host=self.MYSQL_HOST, port=3306, user=self.MYSQL_USER, passwd=self.MYSQL_PWD, db=self.MYSQL_DB)
            # Create cursor
            cursor = db_connect.cursor()
            cursor.execute(sql)
            db_connect.commit()
        except MySQLdb.Error, e:
            logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            print e.args
            print "ERROR: %d: %s" % (e.args[0], e.args[1])

    # def job_logpulsa_to_reminder(self):
    #
    #     al = AnalyticLog()
    #     ml = MongoLog()
    #     for data in al.get_max_pulsa() :
    #         # print str(data['datetime']) + ' ' + str(datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S') + timedelta(days = 30))
    #
    #         self.db.reminder.delete_one({ "msisdn" : data['msisdn'] }) #delete msisdn first
    #         ml.reminder_pulsa(data['msisdn'], "pulsa", data['denom'],
    #         datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S') + timedelta(days = 30), data['phone']) # fill reminder collection
    
    def job_celerylog_to_locationlog(self):

        ml = MongoLog()
        ul = UnstructureLog()
        for data in ul.parse_celery_log('celery1.log'):
            ml.log_location(data[0], data[1][0], data[1][1])
    
    def job_migrate_log_pulsa(self):

        ml = MongoLog()
        sl = StructuredLog()
        data_log = sl.parse_log('../compare_file_to_prod/F_PAID.log', 'PULSA')
        for data in data_log:
            if not data[4].__contains__('PULSA'):
                data_phone = data[4].split('-')
                try:
                    ml.log_pulsa_migrate(data[1], int(data_phone[1]), data[0], data_phone[0])
                except:
                    pass

    def job_loglocation_to_reminder(self):

        ml = MongoLog()
        la = AnalyticLog()
        # query_delete_location = [
        #     {"type_reminder": "location"}
        # ]
        self.db.reminder.delete_many({"type_reminder": "weather"})
        msisdn = []
        for data in la.get_often_location_access():
            if data['_id']['msisdn'] not in msisdn:
                ml.reminder(data['_id']['msisdn'], 'location', data['_id']['location'], '06:00')
            msisdn.append(data['_id']['msisdn'])

    def job_logpulsa_to_phone(self):

        la = AnalyticLog()
        pulsa_data = la.get_pulsa_data()
        for data in pulsa_data:
            msisdn = data['msisdn']
            phone = data['phone']
            count = self.request("select count(1) from phone where msisdn = '%s' and phone = '%s'" % (msisdn, phone))
            if count[0][0] == 0 :
                self.insert("insert into phone (data_date, msisdn, phone) values (now(), '%s', '%s')" % (msisdn, phone))



    def job_logpulsa_to_reminder(self):

        la = AnalyticLog()
        pulsa_data = la.get_pulsa_data()
        range_date = []
        for idx, data in enumerate(pulsa_data):

            date_format = '%Y-%m-%d %H:%M:%S'
            msisdn = data['msisdn']
            phone = data['phone']
            date = datetime.strptime(data['datetime'], date_format)
            next_data = pulsa_data[idx+1]
            next_msisdn = next_data['msisdn']
            next_phone = next_data['phone']
            next_date = datetime.strptime(next_data['datetime'], date_format)
            if msisdn == next_msisdn and phone == next_phone :
                delta_date = date - next_date
                range_date.append(math.fabs(delta_date.days))
            else :
                try :
                    mean_days = numpy.mean(int(math.floor(range_date)))
                except:
                    mean_days = 0
                sql = "select count(1) from reminder A join reminder_ext B  on A.id = B.id "
                "join phone C on B.phone_id = C.id "
                "where A.msisdn = '%s' and C.phone = '%s';" % (msisdn, phone)
                print sql
                count = self.request(sql)
                phone_id = self.request("select id from phone where msisdn = '%s' and phone = '%s' limit 1" % (msisdn, phone))
                curr_date = datetime.now() + timedelta(seconds=1)
                next_run_date = date + timedelta(days=mean_days)
                if count[0][0] == 0:
                    sql = "insert into reminder values ('%s', '%s', "
                    "'1979-08-04 06:00:00', 'tiap', 'No', "
                    "'Sometimes', 'pulsa', '', 'line', '', '7');"
                    "insert into reminder_ext (id, last_run_date, next_run_date, val_iteration, phone_id) "
                    "values ('%s' , '%s', '%s', '%s', '%s');"
                    "" % (curr_date.strftime('%Y%m%d%H%M%S'), msisdn, curr_date.strftime('%Y%m%d%H%M%S'), date, next_run_date, str(mean_days), str(phone_id[0][0]))
                    print sql
                    #self.insert(sql)
                range_date = []

di = DataIntegration()
di.job_logpulsa_to_reminder()