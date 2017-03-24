from datetime import datetime, timedelta
import os
from apscheduler.schedulers.blocking import BlockingScheduler
import MySQLdb
import requests
from log_analytic import AnalyticLog
import urllib
import time
from weather import WeatherService
from bot import Bot
import logging
logging.basicConfig()
from decimal import Decimal
from datetime import datetime
from data_integration import DataIntegration
from gmaps_geolocation import GMapsGeocoding
#First Initialization
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
LINE_TOKEN=""

LINE_IMAGES_ROUTE = "https://bangjoni.com/line_images"

DEBUG_MODE = "D" #I=Info, D=Debug, V=Verbose, E=Error

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
LINE_TOKEN=content[11].split('=')[1]

linebot = Bot(LINE_TOKEN)
weather_service = WeatherService()
gmaps = GMapsGeocoding()
analytic_log = AnalyticLog()
# data_integration = DataIntegration()
#daily -> hanya lihat jam
#once  -> hanya lihat date+jam
#prayer -> hanya lihat jam

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
            linebot.send_text_message(msisdn, desc_reminder)
            if once == "None": 
                insert("delete from reminder where id = '%s' and msisdn = '%s' and platform = 'line'" % (id, msisdn))
            continue
			
        #checking day name for specific day
        if day_system == is_day and time_system == time_reminder:
            print "Got reminder task specific day:", msisdn
            linebot.send_text_message(msisdn, desc_reminder)
            if once == "None": 
                insert("delete from reminder where id = '%s' and msisdn = '%s' and platform = 'line'" % (id, msisdn))
            continue

        #checking time for specific time
        if time_system == time_reminder and dtm.split(' ')[0] == '1979-04-08':
            print "Got reminder task specific time:", msisdn
            linebot.send_text_message(msisdn, desc_reminder)
            if once == "None": 
                insert("delete from reminder where id = '%s' and msisdn = '%s' and platform = 'line'" % (id, msisdn))
            continue


def do_weather_today(msisdn, longitude, latitude):

    (w_now, w_tom) = weather_service.get_wheather(Decimal(longitude), Decimal(latitude))
    if w_now['cuaca'].__contains__('HUJAN'):
        columns = []
        now_actions = []
        column = {}
        column['thumbnail_image_url'] = w_now['image']
        column['title'] = 'Cuaca hari ini'
        column['text'] = "Hari ini rata-rata %s" % (w_now['cuaca'])
        if (len(column['text']) > 60):
            column['text'] = column['text'][:57] + '...'
        w_now.pop('image')
        encoded_url = urllib.urlencode(w_now, doseq=True)
        now_actions.append({'type': 'postback', 'label': 'Detailnya', 'data': encoded_url + "&evt=weather&day_type=today"})
        column['actions'] = now_actions
        columns.append(column)
        linebot.send_composed_carousel(msisdn, "Cuaca", columns)

def get_city_weather():

    sql = "select id, city_name from city"
    sqlout = request(sql)
    insert ("truncate table city_weather")
    for data in sqlout:
        id, city_name = data
        latlng = gmaps.getLatLng(city_name)
        (w_now, w_tom) = weather_service.get_wheather(Decimal(latlng['latitude']), Decimal(latlng['longitude']))
        encoded_url = urllib.urlencode(w_tom, doseq=True)
        insert("insert into city_weather (date_data, id_city, cuaca, deskripsi, image_url) values ('%s', %s, '%s', "
               "'%s', '%s')" % (str(datetime.now()), str(id), str(w_tom['cuaca']), str(encoded_url), str(w_tom['image'])))

# def reminder_cuaca():
#
#     al = AnalyticLog()
#     for data in al.get_reminder_weather():
#         position = data['value'].split(';')
#         do_wheater_today(data['msisdn'], position[0], position[1])


def blast_reminder_weather_service():

    for data in analytic_log.get_reminder_weather():
        position = data['value'].split(';')
        location_detail = gmaps.getLocationDetail(position[0], position[1])
        sql = "select B.cuaca, B.deskripsi, B.image_url " \
              "from city A join city_weather B on A.id = B.id_city " \
              "where lower(A.city_name) = '%s'" % (location_detail['kota'].lower().replace('kota', '').strip())
        sqlout = request(sql)
        cuaca, deskripsi, image_url = sqlout[0]
        columns = []
        now_actions = []
        column = {}
        column['thumbnail_image_url'] = image_url
        column['title'] = 'Cuaca hari ini'
        column['text'] = "Hari ini rata-rata %s" % cuaca
        if (len(column['text']) > 60):
            column['text'] = column['text'][:57] + '...'
        now_actions.append(
            {'type': 'postback', 'label': 'Detailnya', 'data': deskripsi + "&evt=weather&day_type=today"})
        column['actions'] = now_actions
        columns.append(column)
        linebot.send_composed_carousel(data['msisdn'], "Cuaca", columns)


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



#     scheduler = BlockingScheduler()
#     scheduler.add_job(tick, 'interval', minutes=1)
#     # scheduler.add_job(reminder_cuaca, trigger='cron', hour=6) #schedule to reminder weather every 6 am
#     # scheduler.add_job(di.job_celerylog_to_locationlog(), trigger='cron', hour=1)  # schedule to get location user from celery log
#
#     # #print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'$
#     # # linebot.send_message("uba6616c505479974378dadbd15aaeb77", "TEST")
#
#     try:
#         scheduler.start()
#     except (KeyboardInterrupt, SystemExit):
#         pass


    # file = open('uniq_chatid.txt', 'r')
    # i = 0
    # for line in file:
    #     msisdn = str(line).rstrip()
    #     i = i + 1
    #     print "%d send to %s" % (i,msisdn)
    #     sendPhotoTelegram(msisdn, "/tmp/Telegram-Ads-1080-Soccer-v3.png", "")
    #     time.sleep(1)