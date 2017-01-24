from datetime import datetime, timedelta
import os
from apscheduler.schedulers.blocking import BlockingScheduler
import MySQLdb
import requests
import urllib
import time

from bot import Bot
linebot = Bot()
#daily -> hanya lihat jam
#once  -> hanya lihat date+jam
#prayer -> hanya lihat jam

TOKEN_TELEGRAM=""
KEYFILE=""
CERTFILE=""
URL_TELEGRAM=""
MYSQL_HOST=""
MYSQL_USER=""
MYSQL_PWD=""
MYSQL_DB=""
WEB_HOOK=""
EMAIL_NOTIF=""

def request(sql):
    try:
        db_connect = MySQLdb.connect(host = MYSQL_HOST, port = 3306, user = MYSQL_USER, passwd = MYSQL_PWD, db = MYSQL_DB)
        # Create cursor
        cursor = db_connect.cursor()
        cursor.execute(sql)
        sqlout = cursor.fetchall()
        return sqlout
    except MySQLdb.Error, e:
        logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        print e.args
        print "ERROR: %d: %s" % (e.args[0], e.args[1])


def insert(sql):
    try:
        db_connect = MySQLdb.connect(host = MYSQL_HOST, port = 3306, user = MYSQL_USER, passwd = MYSQL_PWD, db = MYSQL_DB)
        # Create cursor
        cursor = db_connect.cursor()
        cursor.execute(sql)
        db_connect.commit()
    except MySQLdb.Error, e:
        logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        print e.args
        print "ERROR: %d: %s" % (e.args[0], e.args[1])


def tick():
    logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S %A')
    date_system = logDtm.split(' ')[0].split('-')[2]
    time_system = logDtm.split(' ')[1]	
    day_system = logDtm.split(' ')[2]	
    print('Tick! The time is: %s %s %s' % (date_system, time_system, day_system))
    time_system = time_system[:5]
	
    sql = "select * from reminder where platform = 'line'"
    sqlout = request(sql)
    for row in sqlout:
        id, msisdn, dtm, once, is_prayer, is_day, description, name, platform, city, gmt = row
        date_reminder = dtm.split(' ')[0].split('-')[2]
        time_reminder = dtm.split(' ')[1]
        time_reminder = time_reminder[:5]
        desc_reminder = "Hi " + name + ", kamu meminta Bang Joni untuk mengingatkan " + description
		
        #checking date for specific date
        if date_system == date_reminder and time_system == time_reminder:
            print "Got reminder task specific date:", msisdn
            linebot.send_message(msisdn, desc_reminder)
            if once == "None": 
                insert("delete from reminder where id = '%s' and msisdn = '%s' and platform = 'line'" % (id, msisdn))
            continue
			
        #checking day name for specific day
        if day_system == is_day and time_system == time_reminder:
            print "Got reminder task specific day:", msisdn
            linebot.send_message(msisdn, desc_reminder)
            if once == "None": 
                insert("delete from reminder where id = '%s' and msisdn = '%s' and platform = 'line'" % (id, msisdn))
            continue

        #checking time for specific time
        if time_system == time_reminder and dtm.split(' ')[0] == '1979-04-08':
            print "Got reminder task specific time:", msisdn
            linebot.send_message(msisdn, desc_reminder)
            if once == "None": 
                insert("delete from reminder where id = '%s' and msisdn = '%s' and platform = 'line'" % (id, msisdn))
            continue			

if __name__ == '__main__':
    ##########OPEN CONFIGURATION#######################
    with open('BJCONFIG.txt') as f:
        content = f.read().splitlines()
    f.close()
    TOKEN_TELEGRAM=content[0].split('=')[1]
    KEYFILE=content[1].split('=')[1]
    CERTFILE=content[2].split('=')[1]
    URL_TELEGRAM=content[3].split('=')[1]
    MYSQL_HOST=content[4].split('=')[1]
    MYSQL_USER=content[5].split('=')[1]
    MYSQL_PWD=content[6].split('=')[1]
    MYSQL_DB=content[7].split('=')[1]
    WEB_HOOK=content[8].split('=')[1]
    EMAIL_NOTIF=content[9].split('=')[1]
	
    scheduler = BlockingScheduler()
    scheduler.add_job(tick, 'interval', minutes=1)
    #print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'$
    linebot.send_message("uba6616c505479974378dadbd15aaeb77", "TEST")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
	
	
    #file = open('uniq_chatid.txt', 'r')
    #i = 0
    #for line in file:
        #msisdn = str(line).rstrip()
        #i = i + 1
        #print "%d send to %s" % (i,msisdn)
        #sendPhotoTelegram(msisdn, "/tmp/Telegram-Ads-1080-Soccer-v3.png", "")
        #time.sleep(1)