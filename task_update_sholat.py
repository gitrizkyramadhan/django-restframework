from datetime import datetime, timedelta
import os
from apscheduler.schedulers.blocking import BlockingScheduler
import MySQLdb
import requests
import urllib
import time
import csv
import httplib2

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

kota_sholat = []
kota_sholat_id = []
kota_sholat_gmt = []


def search_string(mesg, dict):  
    idx = 0
    found = 0
    for item in dict:
        for subitem in item.split('|'):
            if subitem in mesg.lower():
                found = 1
        if found == 1:
             return idx
        idx += 1
    if found == 1:
        return idx
    else:
        return -1 
		
def fetchHTML(url):
    connAPI = httplib2.Http()
    try:
       (resp_headers, content) = connAPI.request(url, "GET")    
       #print ">>resp_header", resp_headers
       return content
    except Exception as e:
       print ">>Error is:",e		
		 
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


def callJadwalSholat(city, cityid, tmz):
    print "UPDATE_SHOLAT: https://sholat.gq/adzan/monthly.php?id=%s" % (cityid)
    #respAPI = fetchHTML("http://sholat.gq/adzan/monthly.php?id=%s" % (cityid))
    respAPI = fetchHTML("http://jadwalsholat.pkpu.or.id/monthly.php?id=%s" % (cityid))
    #print respAPI
    sqlstart = respAPI.find("table_highlight")
    if sqlstart > -1:
        respAPI = respAPI[sqlstart:]
        sqlstop = respAPI.find("</tr>")
        if sqlstop > -1:
            status = respAPI[50:sqlstop]
            if sqlstop > -1:
                #islam_prayer = ['Imsyak','Shubuh','Terbit','Dhuha','Zhuhur','Ashr','Maghrib','Isya']
                islam_prayer = ['Shubuh','Terbit','Dzuhur','Ashr','Maghrib','Isya']	
                i = status.find("<td>")
                j = 0
                while (i > -1):
                    GMT = (7 - tmz)
                    date_object = datetime.strptime('1979-04-08 %s:00' % (status[i+4:i+4+5]), '%Y-%m-%d %H:%M:%S')
                    NewlogDtm = (date_object + timedelta(hours=GMT)).strftime('%Y-%m-%d %H:%M:%S %A')
                    sql = "update reminder set dtm = '%s %s' where city = '%s' and description = '%s'" % (NewlogDtm.split(" ")[0], NewlogDtm.split(" ")[1], city, islam_prayer[j])
                    print "UPDATE_SHOLAT:", sql
                    insert(sql)					
                    status = status[14:]
                    j = j + 1
                    i = status.find("<td>")
                    
                    
def tick():
    logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S %A')
    date_system = logDtm.split(' ')[0]
    time_system = logDtm.split(' ')[1]	
    day_system = logDtm.split(' ')[2]	
    print('UPDATE_SHOLAT: Tick! The time is: %s %s %s' % (date_system, time_system, day_system))
    time_system = time_system[:5]
	
    sql = "select distinct city, gmt from reminder where is_prayer = 'Yes'"
    sqlout = request(sql)
    for row in sqlout:
        city, gmt = row
        print "UPDATE_SHOLAT:", city, gmt
        idx = search_string(city, kota_sholat)
        if idx > -1:
             callJadwalSholat(city, kota_sholat_id[idx], gmt)
        else:
             print "UPDATE_SHOLAT:, Error, no city found"



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
	
    with open('kota_sholat.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            kota_sholat.append(row[1].lower())
            kota_sholat_id.append(row[0].lower())
            kota_sholat_gmt.append(row[3])
	
    tick()
    scheduler = BlockingScheduler()
    scheduler.add_job(tick, 'cron', hour=1)
    #print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'$
    #tick()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
	
