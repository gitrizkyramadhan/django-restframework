from bot import Bot #import class bot line
from datetime import datetime, timedelta # import class datetime dengan method datetime dan timedelta
import MySQLdb
with open('BJCONFIG.txt') as f: #membuka file config BJCONFIG
    content = f.read().splitlines() #membaca file
f.close() #menutup file
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

linebot = Bot(LINE_TOKEN) #inisialisasi class bot dan memasukan parameter toke linebot

# def request(sql): #mmebuat fungsi request untuk mengambil data dari database
#     try: #kalau tidak ada data maka akan masuk ke dalam exception
#         db_connect = MySQLdb.connect(host = MYSQL_HOST, port = 3306, user = MYSQL_USER, passwd = MYSQL_PWD, db = MYSQL_DB) #konek ke database
#         Create cursor
        # cursor = db_connect.cursor()
        # cursor.execute(sql)
        # sqlout = cursor.fetchall()
        # return sqlout
    # except MySQLdb.Error, e:
    #     logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
    #     print e.args
    #     print "ERROR: %d: %s" % (e.args[0], e.args[1])

def getfile_report():
    file = open('report_20170516.txt','r')
    print file

def blast_report(): #membuat fungsi blast report , untuk memblast ke user tertentu


    # msisdn_data = request('select msisdn from yourtable') #query pada table yang berisi msisdn
    msisdn_data = ['U06ebb682542ad76886a4a202d9ac5094','U90a846efb4bc03eec9e66cbf61fea960']
    for msisdn in msisdn_data: #looping setiap user

        linebot.send_text_message(msisdn,'$report_daily') #send message ke user


if __name__ == '__main__':

    # blast_report() #eksekusi method blast

    getfile_report()