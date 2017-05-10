from datetime import datetime, timedelta
import os
from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler
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
from log_mongo import MongoLog
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
mongo_log = MongoLog()
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


def do_weather_today():
    try:
        data = analytic_log.get_max_batchid_track_reminder()
        batchid = int(data[0]['batchid'])
    except:
        batchid = 0
    sql = "select msisdn, city from reminder where description = 'cuaca' and is_day = 'Everyday'"
    sqlout = request(sql)
    hour = datetime.now().hour
    for data in sqlout:
        msisdn, city = data
        try:
            sql = "select B.cuaca, B.deskripsi, B.image_url " \
                  "from city A join city_weather B on A.id = B.id_city " \
                  "where lower(A.city_name) = '%s' and hours = %s" % (city, str(hour))
            sqlout = request(sql)
            cuaca, deskripsi, image_url = sqlout[0]
            if cuaca.__contains__('HUJAN'):
                batchid += 1
                columns = []
                now_actions = []
                column = {}
                column['thumbnail_image_url'] = image_url
                column['title'] = 'Cuaca hari ini'
                column['text'] = "Saat ini perkiraan cuaca di %s akan %s" % (city, cuaca)
                if (len(column['text']) > 60):
                    column['text'] = column['text'][:57] + '...'
                now_actions.append(
                    {'type': 'postback', 'label': 'Detailnya', 'data': deskripsi + "&evt=weather&day_type=reminder_today&city=" + city +
                                                                       "&batchid=" + str(batchid)})
                column['actions'] = now_actions
                columns.append(column)
                try:
                    linebot.send_composed_carousel(msisdn, "Info Cuaca", columns)
                except:
                    pass
                mongo_log.log_track_reminder(batchid, data['msisdn'], 'cuaca', 'daily blast')

        except:
            pass



def get_city_weather():

    hours = [6,16]

    try:
        sql = "select id, city_name from city"
        sqlout = request(sql)
        insert("truncate table city_weather")
        for data in sqlout:
            id, city_name = data
            latlng = gmaps.getLatLng(city_name)
            for data_hour in hours:
                (w_now, w_tom) = weather_service.get_wheather(Decimal(latlng['latitude']), Decimal(latlng['longitude']), data_hour)
                image = str(w_tom['image'])
                w_tom.pop('image')
                encoded_url = urllib.urlencode(w_tom, doseq=True)
                insert("insert into city_weather (date_data, id_city, cuaca, deskripsi, image_url, hours) values ('%s', %s, '%s', "
                       "'%s', '%s', '%s')" % (str(datetime.now()), str(id), str(w_tom['cuaca']), str(encoded_url), image, str(data_hour)))
    except:
        pass

def update_city_reminder():

    try:
        for data in analytic_log.get_reminder_weather():
            position = data['value'].split(';')
            location_detail = gmaps.getLocationDetail(position[0], position[1])
            city = location_detail['kota'].lower().replace('kota', '').strip()
            try:
                insert("update reminder set city = '%s' where msisdn = '%s'" % (data['msisdn'], city))
            except:
                pass
    except:
        pass
# def reminder_cuaca():
#
#     al = AnalyticLog()
#     for data in al.get_reminder_weather():
#         position = data['value'].split(';')
#         do_wheater_today(data['msisdn'], position[0], position[1])


def blast_reminder_weather_service():

    sql_user_after_blast = "select msisdn from reminder where platform = 'line' and description='cuaca' union all select 1 from dual"
    sqlout = request(sql_user_after_blast)
    transform_msisdn = zip(*sqlout)
    msisdn_blast = []
    for data in analytic_log.get_msisdn_blast():
        msisdn_blast.append(data['msisdn'])
    try:
        data = analytic_log.get_max_batchid_track_reminder()
        batchid = int(data[0]['batchid'])
    except:
        batchid = 0
    for data in analytic_log.get_reminder_weather():
        if (data['msisdn'] not in transform_msisdn[0]) and (data['msisdn'] not in msisdn_blast):
            batchid += 1
            position = data['value'].split(';')
            location_detail = gmaps.getLocationDetail(position[0], position[1])
            #city = location_detail['kota'].lower().replace('kota', '').strip()
            try:
                city = location_detail['kota'].lower().replace('kota', '').strip()
                sql = "select B.cuaca, B.deskripsi, B.image_url " \
                      "from city A join city_weather B on A.id = B.id_city " \
                      "where lower(A.city_name) = '%s'" % (city)
                sqlout = request(sql)
                cuaca, deskripsi, image_url = sqlout[0]
                columns = []
                now_actions = []
                yes_action = {'type': 'postback', 'label': 'Yes', 'data': "evt=reminder_weather&confirmation=yes&city=" + city
                                                                          + "&batchid=" + str(batchid)}
                no_action = {'type': 'postback', 'label': 'No', 'data': "evt=reminder_weather&confirmation=no&city=" + city
                                                                        + "&batchid=" + str(batchid)}
                column = {}
                column['thumbnail_image_url'] = image_url
                column['title'] = 'Cuaca hari ini'
                column['text'] = "Hari ini perkiraan cuaca di %s akan %s" % (city, cuaca)
                if (len(column['text']) > 60):
                    column['text'] = column['text'][:57] + '...'
                now_actions.append(
                    {'type': 'postback', 'label': 'Detailnya', 'data': deskripsi + "&evt=weather&day_type=reminder_today"
                                                                                   "&city=" + city + "&batchid=" + str(batchid) })
                column['actions'] = now_actions
                columns.append(column)
                try:
                    linebot.send_composed_carousel(data['msisdn'], "Info Cuaca", columns)
                    linebot.send_composed_confirm(data['msisdn'], 'Info Cuaca',
                                                  'Anyway, gue bisa loh kasih info cuaca kayak gini setiap hari buat lo. Mau nggak? ;)',
                                                  yes_action, no_action)
                except :
                    pass
                mongo_log.log_track_reminder(batchid, data['msisdn'], 'cuaca', 'blast')
                time.sleep(1)
            except:
                pass


def do_reminder_pulsa() :

    sql = "select A.msisdn, C.phone, B.val_iteration from reminder A " \
          "join reminder_ext B on A.id = B.id " \
          "join phone C on B.phone_id = C.id " \
          "where date_format(B.next_run_date, '%Y%m%d') = date_format(now(), '%Y%m%d');"
    sqlout = request(sql)
    try:
        data = analytic_log.get_max_batchid_track_reminder()
        batchid = int(data[0]['batchid'])
    except:
        batchid = 0
    list_msisdn = []
    for data in sqlout:
        msisdn, phone, iteration = data
        if msisdn not in list_msisdn:
            batchid += 1
            yes_action = {'type': 'message', 'label': 'Yes', 'text': "pulsa " + phone}
            no_action = {'type': 'postback', 'label': 'No', 'data': "evt=reminder_pulsa&confirmation=no&phone="
                                                                    + phone + "&batchid=" + str(batchid)}
            list_msisdn.append(msisdn)
            try:
                if iteration in range(1, 8):
                    linebot.send_composed_confirm(msisdn, 'Isi Pulsa',
                                                  'Halo beberapa hari yang lalu pas banget lo '
                                                  'terakhir beli pulsa sama gue ke no ini ' + phone +
                                                  ' . Emang masih ada pulsanya? Mau beli lagi nggak? :)',
                                                  yes_action, no_action)
                    mongo_log.log_track_reminder(batchid, msisdn, 'pulsa', 'blast')
                else:
                    linebot.send_composed_confirm(msisdn, 'Isi Pulsa',
                                                  'Udah lama nggak isi pulsa sama gue nih, '
                                                  'terakhir beli pulsa sama gue ke no ini ' + phone +
                                                  ' . Emang masih ada pulsanya? Mau beli lagi nggak? :)',
                                                  yes_action, no_action)
                    mongo_log.log_track_reminder(batchid, msisdn, 'pulsa', 'blast')
            except:
                pass








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

    do_weather_today()
    # scheduler = BlockingScheduler()
    # #scheduler.add_job(tick, 'interval', minutes=1)
    # scheduler.add_job(get_city_weather, 'cron', hour=21)
    # scheduler.add_job(update_city_reminder, 'cron', hour=23)
    # scheduler.add_job(blast_reminder_weather_service, 'cron', hour=6)
    # scheduler.add_job(do_weather_today, 'cron', hour=12)
    # scheduler.add_job(do_reminder_pulsa, 'cron', hour=14)

    # scheduler.add_job(reminder_cuaca, trigger='cron', hour=6) #schedule to reminder weather every 6 am
    # scheduler.add_job(di.job_celerylog_to_locationlog(), trigger='cron', hour=1)  # schedule to get location user from celery log

    # #print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'$
    # # linebot.send_message("uba6616c505479974378dadbd15aaeb77", "TEST")

    # try:
    #     scheduler.start()
    # except (KeyboardInterrupt, SystemExit):
    #     pass


    # file = open('uniq_chatid.txt', 'r')
    # i = 0
    # for line in file:
    #     msisdn = str(line).rstrip()
    #     i = i + 1
    #     print "%d send to %s" % (i,msisdn)
    #     sendPhotoTelegram(msisdn, "/tmp/Telegram-Ads-1080-Soccer-v3.png", "")
    #     time.sleep(1)