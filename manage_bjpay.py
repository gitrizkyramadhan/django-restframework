#

from nlp_rivescript import Nlp
from datetime import datetime, timedelta
import os
import MySQLdb
import requests
import urllib
import time
from decimal import Decimal
from bjpay_service import BJPayService
from bot import Bot

lineNlp = Nlp()
bjp = BJPayService()
bot = Bot('4NzXHLlCrtqIyNkIizW7Bte1pys9WNUb4Nl1Uv7c2pZNrPZB/D9e2HsbXsUzPyXrcfwzA163oT9a4HkcmkomJwCI6Xn0Rlv/2bmd3numlH2vkosW7TbXZAGFR84/jEn79jiq/hF20HQ5HN0E/x0PPn6Nfd2Y6SKCxBWg7Cr7O3c=')

def update_saldo(msisdn, amount):
    print "=============================================================================================="
    payload = lineNlp.redisconn.get("bjpay/"+msisdn)
    current_balance = int(payload.split('|')[0])
    va_no = payload.split('|')[1]
    phone = payload.split('|')[2]
    print "MSISDN : "+msisdn+", Payload : "+payload
    print "Current balance : " + str(current_balance)
    added_balance = (current_balance+int(amount))
    payload = str(added_balance)+"|" + va_no + "|" + phone
    lineNlp.redisconn.set("bjpay/%s" % (msisdn), payload)
    print "Add "+str(amount)+" to current balance = "+str(added_balance)+", current payload : " + payload

def check_saldo(msisdn):
    print "=============================================================================================="
    payload = lineNlp.redisconn.get("bjpay/" + msisdn)
    print "MSISDN : " + msisdn + ", Payload : " + str(payload)

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

    # lineNlp.redisconn.delete("promo5")
    # print "promo5 deleted"
    # lineNlp.redisconn.delete("promo10")
    # print "promo10 deleted"
    # lineNlp.redisconn.delete("promo20")
    # print "promo20 deleted"
    # lineNlp.redisconn.delete("promo25")
    # print "promo25 deleted"
    # lineNlp.redisconn.delete("promo50")
    # print "promo50 deleted"

    # lineNlp.redisconn.delete("promopulsa50/u40dfa6d04682c9157b32e1654669f3de")
    # lineNlp.redisconn.delete("promopulsa50/uf030ff570c11b82adb3d811118810050")
    # lineNlp.redisconn.delete("promopulsa50/ua13072eb760d4cae5e44bc3735115cf5")
    # print "promopulsa50/u40dfa6d04682c9157b32e1654669f3de deleted"
    # print "promopulsa50/uf030ff570c11b82adb3d811118810050 deleted"
    # print "promopulsa50/ua13072eb760d4cae5e44bc3735115cf5 deleted"

    # lineNlp.redisconn.set("promo5", 0)
    # lineNlp.redisconn.set("promo10", 0)
    # lineNlp.redisconn.set("promo20", 0)
    # lineNlp.redisconn.set("promo25", 0)
    # lineNlp.redisconn.set("promo50", 0)
    # lineNlp.redisconn.set("promo100", 0)


    # print "5K "+lineNlp.redisconn.get("promo5")
    # print "10K "+lineNlp.redisconn.get("promo10")
    # print "20K "+lineNlp.redisconn.get("promo20")
    # print "25K "+lineNlp.redisconn.get("promo25")
    # print "50K "+lineNlp.redisconn.get("promo50")
    # print "100K "+lineNlp.redisconn.get("promo100")

    # lineNlp.redisconn.delete("bjpay/U6fb98eb0f44be13523bbabd566e47dc4")

    # update_saldo('ub08121f3935f74d2f685acc9b2b425ad', 25000) #193

    # print "ALL DONE"

    # check_saldo('u107ce3c78d864298a8aff1824dfdcc61')


def topup_manual(msisdn, phone, amount):
    bjp.credit(msisdn, phone, amount, 1007, 'Topup saldo BJPAY (Manual)')
    (current_balance, va_no, phone) = bjp.get(msisdn)
    bot.send_text_message(msisdn, 'Mohon maaf ya, Bang Joni telat masukin saldo BJPAY kamu, saldo kamu sekarang Rp '+str(current_balance))

def register(msisdn, va_number, phone):
    bjp.register(msisdn, va_number, phone, 0)
    bot.send_text_message(msisdn, 'Mohon maaf ya, Bang Joni udah register lagi BJPAY kamu, sekarang kamu bisa bertransaksi pakai BJPAY')


topup_manual('U6fb98eb0f44be13523bbabd566e47dc4', '085790888409', 10)
register('U6fb98eb0f44be13523bbabd566e47dc4','8650105790888409','085790888409')
