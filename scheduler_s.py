import os
import re
import sys
from time import sleep
from log_mongo import MongoLog
from log_analytic import AnalyticLog
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler()
sched.start()

def reminder_pulsa():
    al = AnalyticLog()
    
    for data in al.get_reminder('pulsa'):
        def print_something():
            print data['msisdn'] + ' ' + data['value']
        sched.add_job(print_something, 'date', run_date=data['date_execution'], )
        
    sched.start()
            

if __name__ == "__main__":
    
    reminder_pulsa()