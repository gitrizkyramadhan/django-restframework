import time
import threading
import sys

from IMAPPush import Idler, idlerInit

from datetime import datetime, timedelta
from nlp_rivescript import Nlp
from html2png import Html2Png
import MySQLdb
import httplib2
import json
import PythonMagick
import pdfkit
import os
import sys
import PyPDF2

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *

import logging
from SimpleXMLRPCServer import SimpleXMLRPCServer
import SocketServer
import thread

import urllib
import requests

from bs4 import BeautifulSoup
import re

from yaml import safe_dump

from utils import fail_print
from utils import response_print
from utils import success_print
from utils import import_app_credentials

from uber_rides.auth import AuthorizationCodeGrant
from uber_rides.client import UberRidesClient
from uber_rides.errors import ClientError
from uber_rides.errors import ServerError
from uber_rides.errors import UberIllegalState

from gevent import pywsgi
from flask import Flask, render_template, request, redirect
import gevent
from gevent import monkey
monkey.patch_all()

#export DISPLAY=127.0.0.1:25.0
#httperf --server www.gopegi.com --port 443 --uri /128131366:AAHlMGVGBLdfRv7hT68r86bv8GXsSuHzjLw --hog --method POST --add-header="Content-type:application/json" --wsesslog=4000,0,test_file.txt --rate=500 --num-conns=500
#https://api.telegram.org/bot128131366:AAHlMGVGBLdfRv7hT68r86bv8GXsSuHzjLw/sendMessage?text=+Oke%2C+Bang+Joni+udah+batalin+pesanan+kamu.+&chat_id=139934550&reply_markup=%7B%22hide_keyboard%22%3A+true%7D
#https://api.telegram.org/bot128131366:AAHlMGVGBLdfRv7hT68r86bv8GXsSuHzjLw/sendPhoto?chat_id=58905239
#/etc/security/limits.conf
#/etc/pam.d/common-session
#POST /bot128131366:AAHlMGVGBLdfRv7hT68r86bv8GXsSuHzjLw/sendMessage?text=Mau+pesen+apa%3F&chat_id=147273983&reply_markup=%7B%22keyboard%22%3A+%5B%5B%22Pesawat%22%2C+%22Kereta%22%2C+%22Xtrans%22%5D%2C+%5B%22Uber%22%2C+%22Info+Restoran%22%2C+%22Info+Tol%22%5D%2C+%5B%22Cuaca%22%5D%5D%7D HTTP/1.1" 200 243
#sendMessage?text=Mau pesen apa?&chat_id=147273983&reply_markup={"keyboard": [["Pesawat", "Kereta", "Xtrans"], ["Uber", "Info Restoran", "Info Tol"], ["Cuaca"]]} 
#/sendMessage?text=Boleh. Untuk berapa orang? (Contoh: 2 dewasa 1 anak 1 bayi)      &chat_id=217234517&reply_markup={"hide_keyboard": true}
#curl -X "POST" https://www.gopegi.com:8443/128131366:AAHlMGVGBLdfRv7hT68r86bv8GXsSuHzjLw -H "Content-Type: application/json" -d '{"message":{"chat":{"id":"999"},"text":"tstrees","location":{"longitude":"","latitude":""},"from":{"username":"","first_name":"","last_name":""},"contact":{"phone_number":"","first_name":"","last_name":""}}}{"message":{"chat":{"id":"999"},"text":"tstrees","location":{"longitude":"","latitude":""},"from":{"username":"","first_name":"","last_name":""},"contact":{"phone_number":"","first_name":"","last_name":""}}}'-d '{"message":{"chat":{"id":"999"},"text":"tstrees","location":{"longitude":"","latitude":""},"from":{"username":"","first_name":"","last_name":""},"contact":{"phone_number":"","first_name":"","last_name":""}}}{"message":{"chat":{"id":"999"},"text":"tstrees","location":{"longitude":"","latitude":""},"from":{"username":"","first_name":"","last_name":""},"contact":{"phone_number":"","first_name":"","last_name":""}}}'
#curl -v -X "POST" http://128.199.88.72:8443/215849274:AAFYj7Aj8zMKt4Zb7TjpONejGuJIPKq2fsI -H "Content-Type: application/json" -d '{"message":{"chat":{"id":"999"},"text":"tstrees","location":{"longitude":"","latitude":""},"from":{"username":"","first_name":"","last_name":""},"contact":{"phone_number":"","first_name":"","last_name":""}}}{"message":{"chat":{"id":"999"},"text":"tstrees","location":{"longitude":"","latitude":""},"from":{"username":"","first_name":"","last_name":""},"contact":{"phone_number":"","first_name":"","last_name":""}}}'-d '{"message":{"chat":{"id":"999"},"text":"tstrees","location":{"longitude":"","latitude":""},"from":{"username":"","first_name":"","last_name":""},"contact":{"phone_number":"","first_name":"","last_name":""}}}{"message":{"chat":{"id":"999"},"text":"tstrees","location":{"longitude":"","latitude":""},"from":{"username":"","first_name":"","last_name":""},"contact":{"phone_number":"","first_name":"","last_name":""}}}'
#curl -X "POST" https://www.gopegi.com/reply.php -H "Content-Type: application/json" -d '{"message":{"chat":{"id":"999"},"text":"tstrees","location":{"longitude":"","latitude":""},"from":{"username":"","first_name":"","last_name":""},"contact":{"phone_number":"","first_name":"","last_name":""}}}{"message":{"chat":{"id":"999"},"text":"tstrees","location":{"longitude":"","latitude":""},"from":{"username":"","first_name":"","last_name":""},"contact":{"phone_number":"","first_name":"","last_name":""}}}'-d '{"message":{"chat":{"id":"999"},"text":"tstrees","location":{"longitude":"","latitude":""},"from":{"username":"","first_name":"","last_name":""},"contact":{"phone_number":"","first_name":"","last_name":""}}}{"message":{"chat":{"id":"999"},"text":"tstrees","location":{"longitude":"","latitude":""},"from":{"username":"","first_name":"","last_name":""},"contact":{"phone_number":"","first_name":"","last_name":""}}}'
#curl -v -X "POST" http://128.199.88.72:8443/215849274:AAFYj7Aj8zMKt4Zb7TjpONejGuJIPKq2fsI -H "Content-Type: application/json" -d '{"message":{"chat":{"id":"999"},"text":"tstrees"}}'

LOG_FILENAME = '/tmp/logging_example.out'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

logging.debug('This message should go to the log file')


incomingClient = {}
uniqClient = {}

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

from bot import Bot
linebot = Bot()

class TelegramGopegi(Nlp, Html2Png, Idler):
    
    def __init__(self):
        print "init at gopegilayer"
		
        self.db_host = MYSQL_HOST
        self.db_port = 3306
        self.db_user = MYSQL_USER
        self.db_pass = MYSQL_PWD
        self.db_name = MYSQL_DB
        # Create Database connection
        #self.initMysql(); 

        Nlp.__init__(self)
        Html2Png.__init__(self)
        Idler.__init__(self)
        
        #self.connAPI = httplib2.Http()  
       
        #self.pdf2jpg = PythonMagick.Image()
        #self.pdf2jpg.density("200")
        self.email_notification = EMAIL_NOTIF
            
    def initMysql(self):
        try:
            self.db_connect = MySQLdb.connect(host = self.db_host, port = self.db_port, user = self.db_user, passwd = self.db_pass, db = self.db_name)
            # Create cursor
            self.cursor = self.db_connect.cursor()
        except MySQLdb.Error, e:
            print e.args
            print 'ERROR: %d: %s' % (e.args[0], e.args[1])
            sys.exit(1)


    def request(self,sql):
        try:
            db_connect = MySQLdb.connect(host = self.db_host, port = self.db_port, user = self.db_user, passwd = self.db_pass, db = self.db_name)
            # Create cursor
            cursor = db_connect.cursor()
            cursor.execute(sql)
            sqlout = cursor.fetchall()
            return sqlout
        except MySQLdb.Error, e:
            logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            print e.args
            print "ERROR: %d: %s" % (e.args[0], e.args[1])
            #print "%s Reconnect Mysql.." % (logDtm)
            #if e.args[0] == 2006:
                #self.initMysql();            

    def insert(self,sql):
        try:
            db_connect = MySQLdb.connect(host = self.db_host, port = self.db_port, user = self.db_user, passwd = self.db_pass, db = self.db_name)
            # Create cursor
            cursor = db_connect.cursor()
            cursor.execute(sql)
            db_connect.commit()
        except MySQLdb.Error, e:
            logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            print e.args
            print "ERROR: %d: %s" % (e.args[0], e.args[1])
            #print "%s Reconnect Mysql.." % (logDtm)
            #if e.args[0] == 2006:
                #self.initMysql();
            


    def fetchJSON(self,url):
        (resp_headers, content) = self.connAPI.request(url, "GET")    

        try:
           decoded = json.loads(content)
           #print json.dumps(decoded, sort_keys=True, indent=4)
           return decoded
        except (ValueError, KeyError, TypeError):
           print "JSON format error"

    def fetchHTML(self,url):
        #connAPI = httplib2.Http()
        try:
           #(resp_headers, content) = connAPI.request(url, "GET")    
           #return content
           r = requests.get(url)
           print "resp html: ", r.content
           return r.content
        except Exception as e:
           print ">>Error is:",e



    def sendMessageTX(self, msisdn, message, keyboard):
        linebot.send_message(msisdn, message.strip())

    def sendPhotoTX(self, msisdn, file_path, caption, keyboard):
        print "---------->", file_path.split('/')[6]
        linebot.send_images(msisdn,"http://128.199.88.72/line_images/%s" % (file_path.split('/')[6]), "http://128.199.88.72/line_images/%s" % (file_path.split('/')[6]))			
	
    def sendMessageT2(self, msisdn, message, keyboard = 0):
        #thread.start_new_thread(self.sendMessageTX, (msisdn, message, keyboard))
        g = gevent.spawn(self.sendMessageTX, msisdn, message, keyboard)

    def sendPhotoT2(self, msisdn, file_path, caption = "", keyboard = 0):
        #thread.start_new_thread(self.sendPhotoTX, (msisdn, file_path, caption, keyboard))
        g = gevent.spawn(self.sendPhotoTX, msisdn, file_path, caption, keyboard) 
		
    def sendPhotoCaptionT2(self, msisdn, link_url, previewImageUrl, message):
        g = gevent.spawn(linebot.send_images_text, msisdn, link_url, previewImageUrl, message.strip())

    def sendRichCaptionT2(self, msisdn, link_url, message, keyboard):
        if keyboard == "tiketux":        
            g = gevent.spawn(linebot.send_rich_message_payment_tiketux_text, msisdn, link_url,"Rich Message", message.strip())
        if keyboard == "tiketdotcom":        
            g = gevent.spawn(linebot.send_rich_message_payment_tiketdotcom_text, msisdn, link_url,"Rich Message", message.strip())
        if keyboard == "tokenpln":        
            g = gevent.spawn(linebot.send_rich_message_token_pln_text, msisdn, link_url,"Rich Message", message.strip())	
        if keyboard == "pulsahp":        
            g = gevent.spawn(linebot.send_rich_message_pulsa_hp_text, msisdn, link_url,"Rich Message", message.strip())				
        if keyboard == "jatis":        
            g = gevent.spawn(linebot.send_rich_message_payment_jatis_text, msisdn, link_url,"Rich Message", message.strip())			
			
    def sendLinkMessageT2(self, msisdn, message1, message2, message3, link_url, previewImageUrl):
        g = gevent.spawn(linebot.send_link_message, msisdn, message1.strip(), message2, message3, link_url, previewImageUrl)
		
    def log_service(self, logDtm, msisdn, first_name, service):      
        sql = "insert into request_service values('" + logDtm + "','" + msisdn + "','" + first_name + "','" + service + "')"
        print sql
        #thread.start_new_thread(self.insert, (sql))

    def verbose(self, mesg):
        print "got message:", mesg

    def get_line_username(self, msisdn):
        sql = "select * from line_users where user_id = '%s'" % (msisdn)
        print sql
        sqlout = self.request(sql)
        first_name = "";
        for row in sqlout:
            first_name = row[1]   
        if first_name != "":
            return first_name
        else:
            r = requests.get("https://api.line.me/v1/profiles?mids=%s" % (msisdn), headers={'Content-Type': 'application/json', 'X-LINE-ChannelToken': 'TyxNuPybSIOEj+GuQXKwktKjGap/+pkSmiK0Baj4HribAaUNAf7CbYLuM/KipVxx5WsoPw5Rw5N5YyNK2wY64un6VMPiQgrowuMpvej/e6XtT1MLps2hS7nYczMxowDqAhj1or15gv5M4TunNRK29K18BSl7lGXPAT9HRw/DX2c='})
            rjson = json.loads(r.content)
            sql = "insert into line_users values('" + msisdn + "','" + rjson["contacts"][0]["displayName"] + "')"
            print sql
            self.insert(sql)  			
            return rjson["contacts"][0]["displayName"]        

    #Telegram busy section    
    def extract_unique_code(text):
        # Extracts the unique_code from the sent /start command.
        return text.split()[1] if len(text.split()) > 1 else None


    def start(self):
        bot.polling()
        while True:
            time.sleep(100)

    
    def onMessage(self, msisdn, ask, first_name):                                     
        if ask[:5] != "[LOC]":
            #ask = ask.translate(None, ",!.?$%").lower()
            #ask = ask.translate(None, "!?$%").lower()
            ask = ask.replace("-"," ")
            ask = ask.replace("!","")
            ask = ask.replace("?","")
            ask = ask.replace("$","")
            ask = ask.replace("\\","")
            ask = ask.replace("%","").lower()
        logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')    
        answer = ""                
        #print logDtm, msisdn, ask
        if self.incomingMsisdn.has_key(msisdn):
            last_request = datetime.strptime(self.incomingMsisdn[msisdn][12],'%Y-%m-%d %H:%M:%S')
            new_request = datetime.strptime(logDtm,'%Y-%m-%d %H:%M:%S')
            if (new_request - last_request).total_seconds() > 1800: #reset request after half an hour
                self.incomingMsisdn[msisdn] = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""]
                answer = self.doNlp("ga jadi", msisdn, first_name)
        else:
            self.incomingMsisdn[msisdn] = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""] 
            
        ask_temp = ask
        if ask[:5] != "[LOC]":
            answer = self.doNlp(ask, msisdn, first_name)
            #print ":", answer
            if (answer[:2] == "ee" and (self.incomingMsisdn[msisdn][11] == "xt01" or self.incomingMsisdn[msisdn][11] == "xt02")):
                ask = self.spell_correctness(ask)
                print "correctness to: ", ask
                answer = self.doNlp(ask, msisdn, first_name)
                self.incomingMsisdn[msisdn][11] == ""
                print "-->", answer

            if answer[:2] == "ee" and self.incomingMsisdn[msisdn][11] == "ke00":
                ask = self.spell_correctness2(ask, self.city_train)
                print "correctness to: ", ask
                answer = self.doNlp(ask, msisdn, first_name)
                if answer[:2] == "ee": 
                    self.incomingMsisdn[msisdn][11] == "ke00"
                else:
                    self.incomingMsisdn[msisdn][11] == ""
                print "-->", answer

            if (answer[:2] == "fl" or answer[:2] == "xt" or answer[:2] == "ke" or answer[:2] == "ub" or answer[:2] == "ca" or answer[:2] == "zo" or answer[:2] == "ch" or answer[:2] == "ee" or answer[:2] == "gr" or answer[:2] == "we" or answer[:2] == "to" or answer[:2] == "ka" or answer[:2] == "sh" or answer[:2] == "eu" or answer[:2] == "re" or answer[:2] == "sh" or answer[:2] == "rs" or answer[:2] == "sc" or answer[:2] == "tr" or answer[:2] == "pl" or answer[:2] == "pu") and self.incomingMsisdn[msisdn][1] != "TRANSLATOR_MODE":
                if answer[:4] != "xt02":
                    temp_answer = answer[4:]
                    temp_answer = temp_answer.replace("xt01 ","")
                    temp_answer = temp_answer.replace("ub01 ","")
                    temp_answer = temp_answer.replace("zo00 ","")
                    temp_answer = temp_answer.replace("ke00 ","")
                    temp_answer = temp_answer.replace("gr01 ","")
                    temp_answer = temp_answer.replace("we01 ","")
                    temp_answer = temp_answer.replace("ka01 ","")
                    temp_answer = temp_answer.replace("tr01 ","")					
                    if answer[:4] != "gr01" and answer[:4] != "ub01" and answer[:4] != "xt08" and answer[:4] != "fl05" and answer[:4] != "ka01" and answer[:4] != "xt01" and answer[:4] != "xt06" and answer[:4] != "xt04" and answer[:4] != "pu01" and answer[:4] != "pl02" and answer[:4] != "pu02":
                        self.sendMessageT2(msisdn, temp_answer, 0)
                    if answer[:4] == "xt08":
                        self.sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/payment_tiketux', answer.replace('xt08 ',''), 'tiketux')					
                    if answer[:4] == "fl05":
                        self.sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/payment_tiketdotcom', answer.replace('fl05 ',''), 'tiketdotcom')										
 
            elif answer[:4] == "xx01":
                if msisdn == "139934550":
                    print "Outgoing---------------------->", logDtm, msisdn, ask, answer
            elif answer[:4] == "xx02":
                logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
                if msisdn == "139934550":
                    print "Outgoing1---------------------->", logDtm, msisdn, ask, answer
                    self.sendPhotoT2(msisdn, 'images/bangjoni.png')
                    self.sendMessageT2(msisdn, answer, 0)
                    logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
                if msisdn == "139934550":
                    print "Outgoing2---------------------->", logDtm, msisdn, ask, answer
            else: 
                if self.incomingMsisdn[msisdn][1] != "TRANSLATOR_MODE":
                    self.sendMessageT2(msisdn, answer, 0)



####################GREETINGS####################
        if answer[:4] == "gr01":
            #photo = open('/home/ubuntu/telegram/images/bangjoni.png', 'rb')
            #bot.send_photo(msisdn, photo)
            #markup = types.ReplyKeyboardMarkup()
            #markup.add('Pesawat', 'Kereta', 'Xtrans', 'Uber', 'Info Restoran', 'Info Tol', 'Cuaca')
            #bot.send_message(msisdn, "Berikut service yang bisa Bang Joni bantu saat ini.", reply_markup=markup)
            #self.sendPhotoT2(msisdn, 'images/bangjoni.png', temp_answer, 1)
            linebot.send_rich_message_greeting_text(msisdn, 'https://www.bangjoni.com/line_images/halo','RICH MESG',temp_answer.strip())
#################################################

####################PULSA START####################
        if answer[:4] == "pu01":
            self.log_service(logDtm, msisdn, first_name, "PULSA")		
            print self.incomingMsisdn[msisdn][2]
            reply = "Berikut harga pulsa %s :\n" % (self.incomingMsisdn[msisdn][2])
            x = ['5K','10K','20K','25K','50K','100K']
            y = [5000,10000,20000,25000,50000,100000]			
            i = 0
            for item in self.incomingMsisdn[msisdn][3].split('|'):
                z = y[i] + int(item)
                if item != "99":
                    reply = reply + x[i] + " Rp. %d" % (z) + "\n"
                i = i + 1
            reply = reply + "Untuk memilih nominal pulsa, tap menu dibawah."
            #print reply
            self.sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/pulsa_hp', reply, 'pulsahp')	
			
        if answer[:4] == "pu02":
            self.sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/payment_jatis', answer[4:], 'jatis')			
            print self.incomingMsisdn[msisdn][1],self.incomingMsisdn[msisdn][5]		
			
        if answer[:4] == "pu03":		
            print self.incomingMsisdn[msisdn][3]		
            params = {'itemtype': self.incomingMsisdn[msisdn][5], 'accountnumber': self.incomingMsisdn[msisdn][1], 'merchantid': 'bangjoni', 'btnsubmit':'Beli'}
            resp = requests.post('http://corepay.mobeli.co.id/jswitch/checkout', data=params)	
            content = resp.text			
            #print content
            soup = BeautifulSoup(content)			
            client_ip = ""				
            id_biller = ""		
            merchant_id = ""
            merchant_code = ""
            basket = ""
            nominal = ""	
            account_number = ""
            item_type = ""		
            production = ""				
			
            try:
                self.incomingMsisdn[msisdn][6] = soup.find('input', {'id': 'client_ip'}).get('value')	
                self.incomingMsisdn[msisdn][7] = soup.find('input', {'id': 'id_biller'}).get('value')
                self.incomingMsisdn[msisdn][8] = soup.find('input', {'id': 'merchant_id'}).get('value')	
                self.incomingMsisdn[msisdn][9] = soup.find('input', {'id': 'merchant_code'}).get('value')
                self.incomingMsisdn[msisdn][10] = soup.find('input', {'id': 'basket'}).get('value')		
                self.incomingMsisdn[msisdn][11] = soup.find('input', {'id': 'nominal'}).get('value')	
                self.incomingMsisdn[msisdn][13] = soup.find('input', {'id': 'account_number'}).get('value')	
                self.incomingMsisdn[msisdn][14] = soup.find('input', {'id': 'item_type'}).get('value')	
                self.incomingMsisdn[msisdn][15] = soup.find('input', {'id': 'production'}).get('value')							
            except:
                print "Error bs4"
			
            sqlstart = content.find("Total Price")
            if sqlstart > -1:
                content = content[sqlstart:]     
                content = content[:content.find("</table>")]		
                total_price = int(re.findall(r'\d+',content)[-1])
                merchantamount = total_price
                print ">>",content, total_price	   
                print self.incomingMsisdn[msisdn]				
			
                params = {'id_biller': self.incomingMsisdn[msisdn][7], 'payment_channel': self.incomingMsisdn[msisdn][3], 'totalamount': total_price}
                print ">>>>>>",params
                resp = requests.post('http://corepay.mobeli.co.id/jswitch/get_pg_amount2', data=params)	
                content = json.loads(resp.text)	
                pgamount = content['pgamount']
                print self.incomingMsisdn[msisdn], total_price, pgamount

                if self.incomingMsisdn[msisdn][3] != "2": #NON ECASH PAYMENT
                    url_pay = 'http://127.0.0.1/pulsa/go_pulsa1.php?payment_channel=%s&client_ip=%s&id_biller=%s&merchant_id=%s&merchant_code=%s&basket=%s&total_price=%s&merchantamount=%s&pgamount=%s&nominal=%s&account_number=%s&item_type=%s&production=%s' % (self.incomingMsisdn[msisdn][3],self.incomingMsisdn[msisdn][6],self.incomingMsisdn[msisdn][7],self.incomingMsisdn[msisdn][8],self.incomingMsisdn[msisdn][9],self.incomingMsisdn[msisdn][10],total_price,merchantamount,pgamount,self.incomingMsisdn[msisdn][11],self.incomingMsisdn[msisdn][13],self.incomingMsisdn[msisdn][14],self.incomingMsisdn[msisdn][15])
                    print url_pay
                    self.sendLinkMessageT2(msisdn, 'berhasil pesen pulsa handphone %s dengan harga %s (include biaya administrasi)' % (self.incomingMsisdn[msisdn][11], pgamount), 'DOKU Payment', 'Bayar Sekarang', url_pay, 'http://128.199.88.72/line_images/logobangjoni2.jpg')				
                else:					
                    params = {'payment_channel': self.incomingMsisdn[msisdn][3], 'client_ip': self.incomingMsisdn[msisdn][6], 'id_biller': self.incomingMsisdn[msisdn][7], 'merchant_id': self.incomingMsisdn[msisdn][8], 'merchant_code': self.incomingMsisdn[msisdn][9], 'basket': self.incomingMsisdn[msisdn][10], 'total_price': total_price, 'merchantamount': merchantamount, 'pgamount': pgamount, 'nominal': self.incomingMsisdn[msisdn][11], 'account_number': self.incomingMsisdn[msisdn][13], 'item_type': self.incomingMsisdn[msisdn][14], 'production': self.incomingMsisdn[msisdn][15]}
                    resp = requests.post('http://127.0.0.1/pulsa/go_pulsa.php', data=params)	
                    content = resp.text
                    #print content

                    sqlstart = content.find("<REDIRECT>https://mandiriecash.com/ecommgateway")
                    if sqlstart > -1:
                        print "eCash PAY"				
                        url_pay = content[sqlstart+10:content.find("</REDIRECT>")]
                        self.sendLinkMessageT2(msisdn, 'berhasil pesen pulsa handphone %s dengan harga %s (include biaya administrasi)' % (self.incomingMsisdn[msisdn][11], pgamount), 'Mandiri eCash', 'Bayar Sekarang', url_pay, 'http://128.199.88.72/line_images/logobangjoni2.jpg')							
						
                sql = "insert into jatis_billers values('" + self.incomingMsisdn[msisdn][1] + "','" + msisdn + "','none','" + logDtm + "','" + self.incomingMsisdn[msisdn][3] + "','')"
                print sql
                self.insert(sql)													
						
            answer = self.doNlp("ga jadi", msisdn, first_name)						
	
				
			
####################TOKEN START####################
        if answer[:4] == "pl01":
            self.log_service(logDtm, msisdn, first_name, "PLN")
            params = {'itemtype': '3|9950102', 'accountnumber': self.incomingMsisdn[msisdn][1], 'merchantid': 'bangjoni', 'btnsubmit':'Beli'}
            resp = requests.post('http://corepay.mobeli.co.id/jswitch/checkout', data=params)	
            content = resp.text
            #print content			
            sqlstart = content.find("NAMA PELANGGAN</b></td><td>:</td><td>")
            if sqlstart > -1:
                content = content[sqlstart+37:]
                sqlstop = content.find("</td></tr>")
                nama_pelanggan_pln = content[:sqlstop]
                daya_pln = content[content.find("TARIF/DAYA</b></td><td>:</td><td>")+33:content.find("VA</td></tr>")+2]

                reply = "Bang Joni dapat info dari PLN, nomor meter tersebut atas nama %s dengan daya %s, tarif token-nya sbb:\n20K Rp. 22.500\n50K Rp. 52.500\n100K Rp. 102.500\n200K Rp. 202.500\n500K Rp. 502.500\n1M Rp. 1.002.500\n5M Rp. 5.002.500\n10M Rp. 10.002.500\n50M Rp. 50.002.500\n\nUntuk memilih tap menu berikut ya" % (nama_pelanggan_pln, daya_pln)
                self.sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/token_pln', reply, 'tokenpln')	
                #content = content[content.find("client_ip\" value=\"")+18:]		
                #print content				
                #client_ip = content[:content.find("\">")]		
                soup = BeautifulSoup(content)	
                client_ip = ""				
                id_biller = ""
                systrace = ""
                inquiryid = ""
                billerid = ""	
                biller_name = ""				
                merchant_id = ""
                merchant_code = ""
                account_number = ""
                item_type = ""		
                production = ""				
                payment_type = ""
			
                try:
                    self.incomingMsisdn[msisdn][4] = soup.find('input', {'id': 'client_ip'}).get('value')	
                    self.incomingMsisdn[msisdn][5] = soup.find('input', {'id': 'id_biller'}).get('value')
                    self.incomingMsisdn[msisdn][6] = soup.find('input', {'id': 'systrace'}).get('value')	
                    self.incomingMsisdn[msisdn][7] = soup.find('input', {'id': 'inquiryid'}).get('value')	
                    self.incomingMsisdn[msisdn][8] = soup.find('input', {'id': 'billerid'}).get('value')	
                    self.incomingMsisdn[msisdn][9] = soup.find('input', {'id': 'biller_name'}).get('value')	
                    self.incomingMsisdn[msisdn][10] = soup.find('input', {'id': 'merchant_id'}).get('value')	
                    self.incomingMsisdn[msisdn][11] = soup.find('input', {'id': 'merchant_code'}).get('value')	
                    self.incomingMsisdn[msisdn][13] = soup.find('input', {'id': 'account_number'}).get('value')	
                    self.incomingMsisdn[msisdn][14] = soup.find('input', {'id': 'item_type'}).get('value')	
                    self.incomingMsisdn[msisdn][15] = soup.find('input', {'id': 'production'}).get('value')	
                    self.incomingMsisdn[msisdn][16] = soup.find('input', {'id': 'payment_type'}).get('value')						
                except:
                    pass				

                print ">>>>",nama_pelanggan_pln, daya_pln, client_ip, id_biller, systrace, inquiryid, billerid, biller_name, merchant_id, merchant_code, account_number, item_type, production, payment_type			
            else:				
                self.sendMessageT2(msisdn, "Nomor meter yang kamu masukkan tidak terdaftar atau salah, coba ulangi lagi ", 0)
                #answer = self.doNlp("ga jadi", msisdn, first_name)				
				
        if answer[:4] == "pl02":				
            self.sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/payment_jatis', answer[4:], 'jatis')	
            print self.incomingMsisdn[msisdn][2]			
			
        if answer[:4] == "pl03":				
            params = {'id_biller': self.incomingMsisdn[msisdn][5], 'payment_channel': self.incomingMsisdn[msisdn][3], 'totalamount': int(self.incomingMsisdn[msisdn][2]) + 2500}
            resp = requests.post('http://corepay.mobeli.co.id/jswitch/get_pg_amount2', data=params)	
            content = json.loads(resp.text)	
            x = content['pgamount']
            print self.incomingMsisdn[msisdn][3], content['pgamount']	

            if self.incomingMsisdn[msisdn][3] != "2": #NON ECASH PAYMENT
                url_pay = 'http://127.0.0.1/pulsa/go_token1.php?totalamount=%s&payment_channel=%s&client_ip=%s&id_biller=%s&systrace=%s&inquiryid=%s&billerid=%s&biller_name=%s&merchant_id=%s&merchant_code=%s&account_number=%s&item_type=%s&production=%s&payment_type=%s&merchantamount=%s&pgamount=%s' % (int(self.incomingMsisdn[msisdn][2]) + 2500, self.incomingMsisdn[msisdn][3],self.incomingMsisdn[msisdn][4],self.incomingMsisdn[msisdn][5],self.incomingMsisdn[msisdn][6],self.incomingMsisdn[msisdn][7],self.incomingMsisdn[msisdn][8],self.incomingMsisdn[msisdn][9],self.incomingMsisdn[msisdn][10],self.incomingMsisdn[msisdn][11],self.incomingMsisdn[msisdn][13],self.incomingMsisdn[msisdn][14],self.incomingMsisdn[msisdn][15],self.incomingMsisdn[msisdn][16], int(self.incomingMsisdn[msisdn][2]) + 2500, content['pgamount'])
                print url_pay
                self.sendLinkMessageT2(msisdn, 'berhasil pesen token listrik %s dengan harga %s (include biaya administrasi)' % (self.incomingMsisdn[msisdn][2], x), 'DOKU Payment', 'Bayar Sekarang', url_pay, 'http://128.199.88.72/line_images/logobangjoni2.jpg')				
            else:
                params = {'totalamount': int(self.incomingMsisdn[msisdn][2]) + 2500, 'payment_channel': self.incomingMsisdn[msisdn][3], 'client_ip': self.incomingMsisdn[msisdn][4], 'id_biller': self.incomingMsisdn[msisdn][5], 'systrace': self.incomingMsisdn[msisdn][6], 'inquiryid': self.incomingMsisdn[msisdn][7], 'billerid': self.incomingMsisdn[msisdn][8], 'biller_name': self.incomingMsisdn[msisdn][9], 'merchant_id': self.incomingMsisdn[msisdn][10], 'merchant_code': self.incomingMsisdn[msisdn][11], 'account_number': self.incomingMsisdn[msisdn][13], 'item_type': self.incomingMsisdn[msisdn][14], 'production': self.incomingMsisdn[msisdn][15], 'payment_type': self.incomingMsisdn[msisdn][16], 'merchantamount': int(self.incomingMsisdn[msisdn][2]) + 2500, 'pgamount': content['pgamount']}
                resp = requests.post('http://127.0.0.1/pulsa/go_token.php', data=params)	
                content = resp.text
                print content

                sqlstart = content.find("<REDIRECT>https://mandiriecash.com/ecommgateway")
                if sqlstart > -1:
                    url_pay = content[sqlstart+10:content.find("</REDIRECT>")]
                    self.sendLinkMessageT2(msisdn, 'berhasil pesen token listrik %s dengan harga %s (include biaya administrasi)' % (self.incomingMsisdn[msisdn][2], x), 'Mandiri eCash', 'Bayar Sekarang', url_pay, 'http://128.199.88.72/line_images/logobangjoni2.jpg')

            sql = "insert into jatis_billers values('" + self.incomingMsisdn[msisdn][1] + "','" + msisdn + "','none','" + logDtm + "','" + self.incomingMsisdn[msisdn][3] + "','')"
            print sql
            self.insert(sql)
				
            answer = self.doNlp("ga jadi", msisdn, first_name)	

####################TRANSLATOR START####################
        if self.incomingMsisdn[msisdn][1] == "TRANSLATOR_MODE":
            self.log_service(logDtm, msisdn, first_name, "TRANSLATOR")		
            self.incomingMsisdn[msisdn][1] = -1
            print "http://127.0.0.1/translator/translate_bing.php?text=%s&lang=%s" % (urllib.quote_plus(ask), self.incomingMsisdn[msisdn][2])
            respAPI = self.fetchHTML("http://127.0.0.1/translator/translate_bing.php?text=%s&lang=%s" % (urllib.quote_plus(ask), self.incomingMsisdn[msisdn][2]))
            print respAPI
            self.sendMessageT2(msisdn, respAPI, 0)			
            return			

        if answer[:4] == "tr01":
            self.incomingMsisdn[msisdn][1] = "TRANSLATOR_MODE"
            print "TRANSLATOR_MODE"
            return


####################CHANGE CITY START####################
        if answer[:4] == "sc01":
            sql = "select * from reminder where msisdn = '%s' and is_prayer = 'No'" % (msisdn)
            print sql
            sqlout = self.request(sql)
            for row in sqlout:
                id, msisdn, dtm, once, is_prayer, is_day, description, name, platform, city, gmt = row
                GMT = (int(gmt) - int(self.incomingMsisdn[msisdn][3]))
                date_object = datetime.strptime('%s' % (dtm), '%Y-%m-%d %H:%M:%S')
                NewlogDtm = (date_object + timedelta(hours=GMT)).strftime('%Y-%m-%d %H:%M:%S %A')
                sql = "update reminder set dtm = '%s %s', city = '%s', gmt = '%s' where msisdn = '%s' and description = '%s' and id = '%s' and is_prayer = 'No'" % (NewlogDtm.split(" ")[0], NewlogDtm.split(" ")[1], self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][3], msisdn, description, id)
                print sql
                self.insert(sql)
				
####################REMINDER SHOLAT START####################
        if answer[:4] == "rs01" or answer[:4] == "sc01":
            self.log_service(logDtm, msisdn, first_name, "SHOLAT")		
            if answer[:4] == "sc01":
                self.incomingMsisdn[msisdn][5] = self.incomingMsisdn[msisdn][3]
                self.incomingMsisdn[msisdn][3] = self.incomingMsisdn[msisdn][2]      
            print "https://sholat.gq/adzan/monthly.php?id=%s" % (self.incomingMsisdn[msisdn][4])
            #respAPI = self.fetchHTML("http://sholat.gq/adzan/monthly.php?id=%s" % (self.incomingMsisdn[msisdn][4]))
            respAPI = self.fetchHTML("http://jadwalsholat.pkpu.or.id/monthly.php?id=%s" % (self.incomingMsisdn[msisdn][4]))
            #print respAPI
            sqlstart = respAPI.find("table_highlight")
            if sqlstart > -1:
                respAPI = respAPI[sqlstart:]
                #print "1>",respAPI
                sqlstop = respAPI.find("</tr>")
                if sqlstop > -1:
                    status = respAPI[50:sqlstop]
                    #print "2>", status
                    if sqlstop > -1:
                        self.insert("delete from reminder where msisdn = '%s' and is_prayer = 'Yes'" % (msisdn))
                        #islam_prayer = ['Imsyak','Shubuh','Terbit','Dhuha','Zhuhur','Ashr','Maghrib','Isya']
                        islam_prayer = ['Shubuh','Terbit','Dzuhur','Ashr','Maghrib','Isya']					
                        str = "Jadwal buka dan sholat %s hari ini:\n\n" % (self.incomingMsisdn[msisdn][3])
                        i = status.find("<td>")
                        j = 0
                        while (i > -1):
                            str = str + islam_prayer[j] + " " + status[i+4:i+4+5] + "\n"

                            GMT = (7 - int(self.incomingMsisdn[msisdn][5]))
                            date_object = datetime.strptime('1979-04-08 %s:00' % (status[i+4:i+4+5]), '%Y-%m-%d %H:%M:%S')
                            NewlogDtm = (date_object + timedelta(hours=GMT)).strftime('%Y-%m-%d %H:%M:%S %A')
                            if islam_prayer[j] != "Terbit" and islam_prayer[j] != "Dhuha" and islam_prayer[j] != "Imsyak":
                                sql = "insert into reminder values('" + logDtm.translate(None, ":- ") + "','" + msisdn + "','" + NewlogDtm.split(" ")[0] + " " + NewlogDtm.split(" ")[1] + "','No','Yes','Everyday','" + islam_prayer[j] + "','" + first_name + "','line','" + self.incomingMsisdn[msisdn][3] + "','" + self.incomingMsisdn[msisdn][5] + "')"
                                print sql
                                self.insert(sql)							
                            
                            status = status[14:]
                            j = j + 1
                            i = status.find("<td>")
                        print ">>> ", str
                        if answer[:4] == "rs01": self.sendMessageT2(msisdn, str, 0)		
		
		

####################REMINDER START####################
        if answer[:4] == "re01":
            self.log_service(logDtm, msisdn, first_name, "REMINDER")		
            if self.incomingMsisdn[msisdn][2] != "None" or self.incomingMsisdn[msisdn][3] != "None" or self.incomingMsisdn[msisdn][4] != "None":
                if self.incomingMsisdn[msisdn][3] == "None":
                    self.incomingMsisdn[msisdn][3] = "04:00:00"
                if self.incomingMsisdn[msisdn][2] == "None":
                    self.incomingMsisdn[msisdn][2] = "1979-08-04"
                GMT = (7 - int(self.incomingMsisdn[msisdn][8]))
                date_object = datetime.strptime('%s %s' % (self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][3]), '%Y-%m-%d %H:%M:%S')
                NewlogDtm = (date_object + timedelta(hours=GMT)).strftime('%Y-%m-%d %H:%M:%S %A')
                sql = "insert into reminder values('" + logDtm.translate(None, ":- ") + "','" + msisdn + "','" + NewlogDtm.split(" ")[0] + " " + NewlogDtm.split(" ")[1] + "','" + self.incomingMsisdn[msisdn][5] + "','No','" + self.incomingMsisdn[msisdn][4] + "','" + self.incomingMsisdn[msisdn][6] + "','" + first_name + "','line','" + self.incomingMsisdn[msisdn][7] + "','" + self.incomingMsisdn[msisdn][8] + "')"
                print sql
                self.insert(sql)
            else:
                self.sendMessageT2(msisdn, self.doNlp("ingetin", msisdn, first_name), 0)             


####################INFO EURO 2016 START####################
        if answer[:4] == "eu01" or answer[:4] == "eu02":
            print "http://www.livescore.com/euro/fixtures/"
            respAPI = self.fetchHTML("http://www.livescore.com/euro/fixtures/")
            #print respAPI
            #sqlstart = respAPI.find("Group stage")
            sqlstart = respAPI.find("Knock-out stage")	
            sqlstop = respAPI.find("timezone")
            fixtures = respAPI[sqlstart:sqlstop]
            fixtures = fixtures.replace("\"","")
            #print fixtures
            if sqlstart > -1:
                str = "\n"
                str1 = "\n"
                while sqlstop > -1:
                    fixtures = fixtures[fixtures.find("<div class=col-8>"):]
                    seri_euro = fixtures[18:fixtures.find("</div>")]
                    fixtures = fixtures[fixtures.find("<div class=col-2>"):]
                    tgl_euro = fixtures[18:fixtures.find("</div>")]
                    fixtures = fixtures[fixtures.find("<div class=col-7>"):]
                    ft_euro = fixtures[56:fixtures.find("</div>")]
                    fixtures = fixtures[fixtures.find("<a href=/euro/match/?match=1"):]
                    url_player_euro = fixtures[8:fixtures.find(">")]
                    fixtures = fixtures[fixtures.find("match="):]
                    player_euro = fixtures[16:fixtures.find("</a>")]
                    fixtures = fixtures[fixtures.find("<div class=col-1 tright>"):]
                    score_euro = fixtures[25:fixtures.find("</div>")]
                    #print ">",seri_euro, tgl_euro, ft_euro, player_euro, score_euro, url_player_euro
                    if ft_euro != "FT" and ft_euro.find("&#x27;") == -1 and ft_euro != "AET":
                        date_select = datetime.strptime(tgl_euro + " " + ft_euro, "%B %d %H:%M")
                        delta = timedelta(hours=7)
                        target_date = date_select + delta
                        tgl_euro = target_date.strftime('%B %d')
                        ft_euro = target_date.strftime('%H:%M')
                    if ft_euro.find("&#x27;") > -1:
                        ft_euro = ft_euro.replace("&#x27;"," min (LIVE)")
                        print "------------------>", ft_euro
                    str = str + tgl_euro + " " + ft_euro + ":\n"
                    str = str + player_euro + " " + score_euro + "\n\n"
                    sqlstop = fixtures.find("match=")

                    if answer[:4] == "eu02" and player_euro.lower().find(self.incomingMsisdn[msisdn][3]) > -1:
                        #print ">>", player_euro
                        str1 = str1 + tgl_euro + " " + ft_euro + ":\n"
                        str1 = str1 + player_euro + " " + score_euro + "\n"
                        player1 = player_euro.split("vs")[0]
                        player2 = player_euro.split("vs")[1]
                        print "http://www.livescore.com%s" % (url_player_euro)
                        respAPI = self.fetchHTML("http://www.livescore.com%s" % (url_player_euro))
                        respAPI = respAPI.replace("\"","")
                        y = respAPI
					
                        #find player1 goal
                        sqlstart = respAPI.find("</span> <span class=ml4></span> <span class=inc goal></span>")
                        #print respAPI
                        while sqlstart > -1:
                            x = respAPI[:sqlstart]
                            #print "]]]]]1>", sqlstart, respAPI[sqlstart-10:sqlstart]
                            str1 = str1 + respAPI[x.rfind("<span class=name name-large>")+28:sqlstart] + " (" + player1 + " Goal)\n"
                            respAPI = respAPI[sqlstart+1:]
                            sqlstart = respAPI.find("</span> <span class=ml4></span> <span class=inc goal></span>")

                        #find player2 goal
                        respAPI = y
                        sqlstart = respAPI.find("<span class=inc goal></span> <span class=mr4></span> <span class=name name-large>")
                        #print respAPI
                        while sqlstart > -1:	
                            #print "]]]]]2>", sqlstart, respAPI[sqlstart+81:10]						
                            respAPI = respAPI[sqlstart+81:]
                            str1 = str1 + respAPI[:respAPI.find("</span>")] + " (" + player2 + " Goal)\n"
                            sqlstart = respAPI.find("<span class=inc goal></span> <span class=mr4></span> <span class=name name-large>")
							
                        str1 = str1 + "\n"
                
                if answer[:4] == "eu01":
                    str = str.replace("? - ?","")
                    str = str + "\nKamu bisa juga mengetahui nama pemain yang mencetak goal, cukup sebut negaranya."
                    self.sendMessageT2(msisdn, str, 0)
                else:
                    self.sendMessageT2(msisdn, str1, 0)
			
####################INFO EURO 2016 END##############

####################WAKTU SHOLAT####################
        if answer[:4] == "sh01":
            self.log_service(logDtm, msisdn, first_name, "SHOLAT")		
            print "https://sholat.gq/adzan/monthly.php?id=%s" % (self.incomingMsisdn[msisdn][4])
            #respAPI = self.fetchHTML("http://sholat.gq/adzan/monthly.php?id=%s" % (self.incomingMsisdn[msisdn][4]))   
            respAPI = self.fetchHTML("http://jadwalsholat.pkpu.or.id/monthly.php?id=%s" % (self.incomingMsisdn[msisdn][4]))
            #print respAPI 
            sqlstart = respAPI.find("table_highlight")
            if sqlstart > -1:
                respAPI = respAPI[sqlstart:]
                #print "1>",respAPI
                sqlstop = respAPI.find("</tr>")				
                if sqlstop > -1:
                    status = respAPI[50:sqlstop]     
                    #print "2>", status
                    if sqlstop > -1:
                        #islam_prayer = ['Imsyak','Shubuh','Terbit','Dhuha','Zhuhur','Ashr','Maghrib','Isya']
                        islam_prayer = ['Shubuh','Terbit','Dzuhur','Ashr','Maghrib','Isya']	
                        str = "Jadwal buka dan sholat %s hari ini:\n\n" % (self.incomingMsisdn[msisdn][3])
                        i = status.find("<td>")
                        j = 0
                        while (i > -1):
                            str = str + islam_prayer[j] + " " + status[i+4:i+4+5] + "\n"
                            status = status[14:]
                            j = j + 1
                            i = status.find("<td>")
                        print ">>> ", str
                        self.sendMessageT2(msisdn, str, 0)						
                    
		
		
####################KASKUS####################
        if answer[:4] == "ka01":
            self.sendPhotoT2(msisdn, 'images/kaskus_movie.jpg', temp_answer, 0)
#################################################

####################LOG UNIDENTIFY USER RESPONSE####################
        if answer[:4] == "ee01":
            sql = "insert into unknown_asking values('" + logDtm + "','" + msisdn + "','" + self.incomingMsisdn[msisdn][27] + "','" + ask_temp + "','" + ask + "')"
            print sql
            self.insert(sql)   
        else:
            self.incomingMsisdn[msisdn][27] = answer

####################CANCEL MODULE START####################
        if answer[:4] == "ca01":
            try:
                del self.incomingMsisdn[msisdn]  
                del self.bookingMsisdn[msisdn]
                print "Done cancel order"
            except:
                print "Error cancel order"

###########################################################

####################CHANGE MODULE START####################
        if answer[:4] == "ch01" or answer[:4] == "ch02":
            print "switch merchant conversation"
            find_trigger = answer.find("xt01")
            if find_trigger != -1:
                answer = answer[find_trigger:]
                print answer
            find_trigger = answer.find("ub01")
            if find_trigger != -1:
                answer = answer[find_trigger:]
                print answer
            find_trigger = answer.find("zo00")
            if find_trigger != -1:
                answer = answer[find_trigger:]
                print answer
            find_trigger = answer.find("ke00")
            if find_trigger != -1:
                answer = answer[find_trigger:]
                print answer
            find_trigger = answer.find("we01")
            if find_trigger != -1:
                answer = answer[find_trigger:]
                print answer
            
            #Cancel uber request ride
            if answer[:4] == "ch02" and self.incomingMsisdn[msisdn][6] != -1 and self.incomingMsisdn[msisdn][7] != -1:
                print "http://127.0.0.1/uber/cancel_ride.php?request_id=%s&access_token=%s" % (self.incomingMsisdn[msisdn][6], self.incomingMsisdn[msisdn][7])
                respAPI = self.fetchHTML("http://127.0.0.1/uber/cancel_ride.php?request_id=%s&access_token=%s" % (self.incomingMsisdn[msisdn][6], self.incomingMsisdn[msisdn][7]))   
                print respAPI 

            self.incomingMsisdn[msisdn] = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""]             
###########################################################

####################INFO TOL MODULE START####################
        if answer[:4] == "to01":
            self.log_service(logDtm, msisdn, first_name, "TOL")
            sql = "select * from tol_jasamarga where pintu = '%s'" % (self.incomingMsisdn[msisdn][2])
            print sql
            sqlout = self.request(sql)
            ruas_tol = "";
            for row in sqlout:
                ruas_tol = row[0]

            if ruas_tol != "":
                print "http://127.0.0.1/twitter/jasamarga.php?ruas=%s&gate=%s" % (urllib.quote_plus(ruas_tol), urllib.quote_plus(self.incomingMsisdn[msisdn][2]))
                respAPI = self.fetchHTML("http://127.0.0.1/twitter/jasamarga.php?ruas=%s&gate=%s" % (urllib.quote_plus(ruas_tol), urllib.quote_plus(self.incomingMsisdn[msisdn][2])))
                print respAPI
                info_tol = ""
                sqlstart = respAPI.find("<jasamarga>")
                sqlstop = respAPI.find("</jasamarga>") - 1
                info_tol = respAPI[sqlstart+11:sqlstop]
                print info_tol
                if sqlstart > -1:
                    jam_update = info_tol.split(" ")[0]
                    x = 0
                    s = ""
                    for item in info_tol.split(" "):
                        if x >= 3:
                            s = s + item + " "
                        x = x + 1
                    sinfo_tol = "Dari Jasa marga, berikut info tol %s, jam %s WIB:" % (self.incomingMsisdn[msisdn][2], jam_update)
                    self.sendMessageT2(msisdn.decode('utf-8'), sinfo_tol + "\n" + s, 0)

                    info_tol_media = ""
                    sqlstart = respAPI.find("<jasamarga_media>")
                    sqlstop = respAPI.find("</jasamarga_media>") - 1
                    info_tol_media = respAPI[sqlstart+17:sqlstop]
                    if sqlstart > -1:
                        for item in info_tol_media.split('|'):
                            print "info tol media url:",item
                            f = open('/tmp/' + item.split('/')[-1],'wb')
                            f.write(urllib.urlopen(item).read())
                            f.close()
                            #photo = open('/tmp/' + item.split('/')[-1], 'rb')
                            self.sendPhotoT2(msisdn, '/tmp/' + item.split('/')[-1])
                else:
                    self.sendMessageT2(msisdn, "Sorry " + first_name + ", Bang Joni belum update infonya, coba aja ruas tol lainnya", 0)

####################INFO TOL MODULE END####################

####################WEATHER MODULE START####################
        if answer[:4] == "we01":
            print "xxxxxxxxxxxxxxx1"
            self.log_service(logDtm, msisdn, first_name, "CUACA")
            self.incomingMsisdn[msisdn][11] = "we01"
            print "xxxxxxxxxxxxxxx2"

        if ask[:5] == "[LOC]" and self.incomingMsisdn[msisdn][11] == "we01":
            self.incomingMsisdn[msisdn][11] == "";
            self.incomingMsisdn[msisdn][2]  = ask[5:].split(';')[0]
            self.incomingMsisdn[msisdn][3]  = ask[5:].split(';')[1]

            print "http://gopegi.com/weather/weather1.php?latlong=%s,%s" % (self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][3])
            respAPI = self.fetchHTML("http://gopegi.com/weather/weather1.php?latlong=%s,%s" % (self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][3]))
            print respAPI
            weather_forecast = ""
            sqlstart = respAPI.find("<weather>")
            sqlstop = respAPI.find("</weather>") - 1
            weather_forecast = respAPI[sqlstart+9:sqlstop]
            if sqlstart > -1:
               print weather_forecast
               weather_forecasts = weather_forecast.split('|')
               time_updated = weather_forecasts[0]
               suhu = weather_forecasts[1]
               cuaca = weather_forecasts[2].upper()
               kec_angin = weather_forecasts[3]
               humidity = weather_forecasts[4]

               tom_cuaca = weather_forecasts[5].upper()
               tom_suhu_min = weather_forecasts[6]
               tom_suhu_max = weather_forecasts[7]
               tom_sunrise = weather_forecasts[8]
               tom_sunset = weather_forecasts[9]
               self.sendMessageT2(msisdn, first_name +  ", cuaca hari ini %s dengan suhu rata2 %s Celcius dan kecepatan angin %s Km/h.\nPerkiraan cuaca untuk besok adalah %s, dengan suhu minimal %s Celcius dan suhu maksimal %s Celcius" % (cuaca, suhu, kec_angin, tom_cuaca, tom_suhu_min, tom_suhu_max), 0)

####################WEATHER MODULE END####################


####################ZOMATO MODULE START####################
        if answer[:4] == "zo00":
            self.log_service(logDtm, msisdn, first_name, "ZOMATO")
            self.incomingMsisdn[msisdn][11] = "zo00"

        if ask[:5] == "[LOC]" and self.incomingMsisdn[msisdn][11] == "zo00":
            self.incomingMsisdn[msisdn][11] == "";
            self.incomingMsisdn[msisdn][2]  = ask[5:].split(';')[0]
            self.incomingMsisdn[msisdn][3]  = ask[5:].split(';')[1]
            #self.sendMessageT2(msisdn, "Ok, Bang Joni sudah tahu lokasimu, sekarang kamu pingin masakan apa?", 0)
            #photo = open('/home/ubuntu/telegram/images/zomato_cuisines.png', 'rb')
            #self.sendPhotoT2(msisdn, 'images/zomato_cuisines.png')
            self.sendPhotoCaptionT2(msisdn, "https://www.bangjoni.com/line_images/zomato_cuisines.jpg", "https://www.bangjoni.com/line_images/zomato_cuisines.jpg", "Ok, Bang Joni sudah tahu lokasimu, sekarang kamu pingin masakan apa?")


        if answer[:4] == "zo01" or answer[:4] == "zo02":
            if answer[:4] == "zo01":
                print "http://127.0.0.1/zomato/search_restaurant.php?location=%s&cuisine=%s" % (self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][3])
                respAPI = self.fetchHTML("http://127.0.0.1/zomato/search_restaurant.php?location=%s&cuisine=%s" % (self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][3]))
            else:
                print "http://127.0.0.1/zomato/search_restaurant_longlat.php?long=%s&lat=%s&cuisines_id=%s" % (self.incomingMsisdn[msisdn][3], self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][4])
                respAPI = self.fetchHTML("http://127.0.0.1/zomato/search_restaurant_longlat.php?long=%s&lat=%s&cuisines_id=%s" % (self.incomingMsisdn[msisdn][3], self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][4]))
            print respAPI
            list_restaurants = ""
            sqlstart = respAPI.find("<found>")
            sqlstop = respAPI.find("</found>") - 1
            list_restaurants = respAPI[sqlstart+7:sqlstop]
            if list_restaurants != "":
                for item in list_restaurants.split(';'):
                    #print item.split('|')[2]
                    respAPI = self.fetchHTML(item.split('|')[2])
                    list_menu = ""
                    sqlstart = respAPI.find("zomato.menuPages")
                    sqlstop = respAPI.find("zomato.menuTypes") - 1
                    list_menu = respAPI[sqlstart+16:sqlstop]
                    if sqlstart != -1:
                        jpg_menu = list_menu.split(',')[0].split(':')[2]
                        jpg_menu = jpg_menu.translate(None, "\\\"")
                        print jpg_menu
                        print jpg_menu.split('/')[-1]
                        answer = item.split('|')[0] + "\n" + item.split('|')[1]
                        #self.sendMessageT2(msisdn, answer, 0)

                        f = open('/usr/share/nginx/html/line_images/' + jpg_menu.split('/')[-1],'wb')
                        f.write(urllib.urlopen('https:' + jpg_menu).read())
                        f.close()

                        #photo = open('/tmp/' + jpg_menu.split('/')[-1], 'rb')
                        #self.sendPhotoT2(msisdn, '/usr/share/nginx/html/line_images/' + jpg_menu.split('/')[-1], answer)
                        self.sendPhotoCaptionT2(msisdn, "http://128.199.88.72/line_images/%s" % (jpg_menu.split('/')[-1]), "http://128.199.88.72/line_images/%s" % (jpg_menu.split('/')[-1]), answer)
            else:
                self.sendMessageT2(msisdn, "Bang Joni tidak menemukan rekomendasi restoran dari zomato, coba cari tempat atau cuisine lainnya", 0)

####################ZOMATO MODULE END####################

####################XTRANS MODULE START####################
        if answer[:4] == "xt01":
            #photo = open('/home/ubuntu/telegram/images/xtrans_pool.png', 'rb')
            self.log_service(logDtm, msisdn, first_name, "XTRANS")
            self.sendPhotoCaptionT2(msisdn, 'http://128.199.88.72/line_images/Pool_Xtrans.jpg', 'http://128.199.88.72/line_images/Pool_Xtrans.jpg', answer.replace("xt01 ",""))
            self.incomingMsisdn[msisdn][11] = "xt01"


        if answer[:4] == "xt02":
            self.incomingMsisdn[msisdn][11] = "xt02"
            if self.incomingMsisdn[msisdn][3] == "semanggi": self.incomingMsisdn[msisdn][3] = self.incomingMsisdn[msisdn][3] + "/ kc"			
            sql = "select * from searching_xtrans where msisdn = '%s' and cabangtujuan ='%s'" % (msisdn, self.incomingMsisdn[msisdn][3])
            print sql
            sqlout = self.request(sql)
            kode_jurusan = "";
            for row in sqlout:
                kode_jurusan = row[1]
                kota_asal = row[3]
                cabang_asal = row[4]
                kota_tujuan = row[5]
                cabang_tujuan = row[6]

            if kode_jurusan == "":
                answer = answer[4:] + "\n"
                if self.incomingMsisdn[msisdn][3] == "semanggi": self.incomingMsisdn[msisdn][3] = self.incomingMsisdn[msisdn][3] + "/ kc"
                print "http://127.0.0.1/tiketux/jurusan.php?d=%s" % (urllib.quote_plus(self.incomingMsisdn[msisdn][3]))
                respAPI = self.fetchHTML("http://127.0.0.1/tiketux/jurusan.php?d=%s" % (urllib.quote_plus(self.incomingMsisdn[msisdn][3])))
                print respAPI
                if len(respAPI) > 5:  
                    self.insert("delete from searching_xtrans where msisdn = '%s'" % (msisdn))
                    respAPI = respAPI[:len(respAPI)-1]
                    for cabangtujuan in respAPI.split('|'):
                        xtrans_id, xtrans_kode, xtrans_kotaAsal, xtrans_cabangAsal, xtrans_kotaTujuan, xtrans_cabangTujuan = cabangtujuan.split(';')
                        print xtrans_cabangTujuan
                        sql = "insert into searching_xtrans values('" + msisdn + "','" + xtrans_id + "','" + xtrans_kode + "','" + xtrans_kotaAsal + "','" + xtrans_cabangAsal.lower() + "','" + xtrans_kotaTujuan + "','" + xtrans_cabangTujuan.lower() + "')"
                        print sql
                        self.insert(sql)  
                        answer = answer + xtrans_cabangTujuan + "\n"
            else:
                self.insert("delete from searching_xtrans where msisdn = '%s'" % (msisdn))
                self.incomingMsisdn[msisdn][3] = kode_jurusan
                self.incomingMsisdn[msisdn][4] = kota_asal
                self.incomingMsisdn[msisdn][5] = cabang_asal
                self.incomingMsisdn[msisdn][6] = kota_tujuan
                self.incomingMsisdn[msisdn][7] = cabang_tujuan
                ask = "xt02aa"
                answer = self.doNlp(ask, msisdn, first_name)

            self.sendMessageT2(msisdn, answer, 0)

        if answer[:4] == "xt03":
            self.incomingMsisdn[msisdn][11] = ""
            ask = "xt03"
            answer = self.doNlp(ask, msisdn, first_name)   
            #self.sendMessageT2(msisdn, answer, 0)
            print "http://127.0.0.1/tiketux/jadwal_xtrans.php?jurusan=%s&tgl=%s&asal=%s&tujuan=%s" % (self.incomingMsisdn[msisdn][3], self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][5], self.incomingMsisdn[msisdn][7])
            respAPI = self.fetchHTML("http://127.0.0.1/tiketux/jadwal_xtrans.php?jurusan=%s&tgl=%s&asal=%s&tujuan=%s" % (self.incomingMsisdn[msisdn][3], self.incomingMsisdn[msisdn][2], urllib.quote_plus(self.incomingMsisdn[msisdn][5]), urllib.quote_plus(self.incomingMsisdn[msisdn][7])))

            sqlstart = respAPI.find("<SQL>")
            sqlstop = respAPI.find("</SQL>")
            list_airlines = respAPI[sqlstart+5:sqlstop]
            if len(list_airlines) > 10:  

                fo = open('/tmp/%s_cari.html' % (msisdn), "w")
                fo.write(respAPI)
                fo.close()
                options = {
                    'page-size': 'A6',
                    'margin-top': '0',
                    'margin-right': '0',
                    'margin-bottom': '0',
                    'margin-left': '0',
                    'encoding': "UTF-8"
                }
                try:
                    pdfkit.from_file('/tmp/%s_cari.html' % (msisdn), '/usr/share/nginx/html/line_images/%s_cari.pdf' % (msisdn), options=options)
                except Exception as e:
                    print "Error pdfkit",e
                if os.path.exists('/usr/share/nginx/html/line_images/%s_cari.pdf' % (msisdn)): 
                    outfile = '/usr/share/nginx/html/line_images/%s_cari.pdf' % (msisdn)
                    pdf2jpg = PythonMagick.Image()
                    pdf2jpg.density("200")
                    pdf2jpg.read(outfile)
                    randomDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y%m%d%H%M%S')	
                    pdf2jpg.write("%s_%s.jpg" % (outfile.split('.')[0], randomDtm))  
                    print "Done convert html to pdf to png"                                                
                    #photo = open('%s.jpg' % (outfile.split('.')[0]), 'rb')
                    #self.sendPhotoT2(msisdn, '%s.jpg' % (outfile.split('.')[0]))
                    self.sendPhotoCaptionT2(msisdn, 'http://128.199.88.72/line_images/%s_%s.jpg' % (outfile.split('.')[0].split('/')[6], randomDtm), 'http://128.199.88.72/line_images/%s_%s.jpg' % (outfile.split('.')[0].split('/')[6], randomDtm), answer)					

                    self.insert("delete from searching_jadwal_xtrans where msisdn = '%s'" % (msisdn))
                    list_airlines = list_airlines[:len(list_airlines)-1]
                    for cabangtujuan in list_airlines.split(','):
                        no, kode, jam_berangkat, layout_kursi, jumlah_kursi, jumlah_booking, harga = cabangtujuan.split(';')
                        sql = "insert into searching_jadwal_xtrans values('" + msisdn + "','" + no + "','" + kode + "','" + jam_berangkat + "','" + layout_kursi + "','" + jumlah_kursi + "','" + jumlah_kursi + "','" + harga + "')"
                        #print sql
                        self.insert(sql)   
            else:
                self.sendMessageT2(msisdn, "Bang Joni tidak menemukan jadwalnya, coba cari tanggal lainnya...", 0)

        if answer[:4] == "xt04":
            self.incomingMsisdn[msisdn][11] = ""
            answer = answer + "\n%s penumpang dengan format: " % (self.incomingMsisdn[msisdn][1])
            for i in range(self.incomingMsisdn[msisdn][1]):
                answer = answer + "nama lengkap " + `i+1` + ","
            answer = answer[:len(answer)-1]
            self.sendMessageT2(msisdn, answer.replace('xt04 ',''), 0)

            
        if answer[:4] == "xt06":
            self.incomingMsisdn[msisdn][11] = ""
            answertemp = answer
            ask = "xt06aa"
            answer = self.doNlp(ask, msisdn, first_name)
            sql = "select * from searching_jadwal_xtrans where msisdn = '%s' and no = %s" % (msisdn, self.incomingMsisdn[msisdn][10])
            print sql
            sqlout = self.request(sql)
            kode = ""
            for row in sqlout:
                kode = row[2]
                layout_kursi = row[4]
            if kode != "":
                self.incomingMsisdn[msisdn][4] = kode
                self.incomingMsisdn[msisdn][6] = layout_kursi

            print "http://127.0.0.1/tiketux/layout_kursi.php?kode=%s&tgl=%s&jadwal=%s" % (self.incomingMsisdn[msisdn][6], self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][4])
            respAPI = self.fetchHTML("http://127.0.0.1/tiketux/layout_kursi.php?kode=%s&tgl=%s&jadwal=%s" % (self.incomingMsisdn[msisdn][6], self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][4]))
            if 1:   

                fo = open('/tmp/%s_cari.html' % (msisdn), "w")
                fo.write(respAPI)
                fo.close()
                options = {
                    'page-size': 'A6',
                    'margin-top': '0',
                    'margin-right': '0',
                    'margin-bottom': '0',
                    'margin-left': '0',
                    'encoding': "UTF-8"
                }
                try:
                    pdfkit.from_file('/tmp/%s_cari.html' % (msisdn), '/usr/share/nginx/html/line_images/%s_cari.pdf' % (msisdn), options=options)
                except Exception as e:
                    print "Error pdfkit",e
                if os.path.exists('/usr/share/nginx/html/line_images/%s_cari.pdf' % (msisdn)): 
                    outfile = '/usr/share/nginx/html/line_images/%s_cari.pdf' % (msisdn)
                    pdf2jpg = PythonMagick.Image()
                    pdf2jpg.density("200")
                    pdf2jpg.read(outfile)
                    randomDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y%m%d%H%M%S')	
                    pdf2jpg.write("%s_%s.jpg" % (outfile.split('.')[0], randomDtm))  
                    print "Done convert html to pdf to png"                                                
                    #photo = open('%s.jpg' % (outfile.split('.')[0]), 'rb')
                    #self.sendPhotoT2(msisdn, '%s.jpg' % (outfile.split('.')[0]))
                    self.sendPhotoCaptionT2(msisdn, 'http://128.199.88.72/line_images/%s_%s.jpg' % (outfile.split('.')[0].split('/')[6], randomDtm), 'http://128.199.88.72/line_images/%s_%s.jpg' % (outfile.split('.')[0].split('/')[6], randomDtm), answertemp.replace("xt06 ",""))

        if answer[:4] == "xt09": 
            self.incomingMsisdn[msisdn][11] = ""
            print "--------------> ",self.incomingMsisdn[msisdn][3]
            #print "http://127.0.0.1/tiketux/booking.php?jadwal=%s&tanggal_berangkat=%s&nomor_kursi=%s&nama_penumpang=%s&nama_pemesan=%s&alamat_pemesan=%s&telp_pemesan=%s&email_pemesan=%s&channel=BGJ&payment=fin195" % (self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][2], urllib.quote_plus(self.incomingMsisdn[msisdn][3]), urllib.quote_plus(self.incomingMsisdn[msisdn][9]), urllib.quote_plus('elina wardhani'), urllib.quote_plus('cibubur bogor'), urllib.quote_plus('08119772759'), urllib.quote_plus(EMAIL_NOTIF))
            #respAPI = self.fetchHTML("http://127.0.0.1/tiketux/booking.php?jadwal=%s&tanggal_berangkat=%s&nomor_kursi=%s&nama_penumpang=%s&nama_pemesan=%s&alamat_pemesan=%s&telp_pemesan=%s&email_pemesan=%s&channel=BGJ&payment=fin195" % (self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][3], urllib.quote_plus(self.incomingMsisdn[msisdn][9]), urllib.quote_plus('elina wardhani'), urllib.quote_plus('cibubur bogor'), urllib.quote_plus('08119772759'), urllib.quote_plus(EMAIL_NOTIF)))
            print "http://127.0.0.1/tiketux/booking1.php?jadwal=%s&tanggal_berangkat=%s&nomor_kursi=%s&nama_penumpang=%s&nama_pemesan=%s&alamat_pemesan=%s&telp_pemesan=%s&email_pemesan=%s&channel=BGJ&payment=%s" % (self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][2], urllib.quote_plus(self.incomingMsisdn[msisdn][3]), urllib.quote_plus(self.incomingMsisdn[msisdn][9]), urllib.quote_plus(self.incomingMsisdn[msisdn][9].split(",")[0]), urllib.quote_plus('Bang Joni, Palma One 2nd floor suit 210 Jakarta Selatan'), urllib.quote_plus(self.incomingMsisdn[msisdn][7]), urllib.quote_plus(EMAIL_NOTIF), self.incomingMsisdn[msisdn][5])
            respAPI = self.fetchHTML("http://127.0.0.1/tiketux/booking1.php?jadwal=%s&tanggal_berangkat=%s&nomor_kursi=%s&nama_penumpang=%s&nama_pemesan=%s&alamat_pemesan=%s&telp_pemesan=%s&email_pemesan=%s&channel=BGJ&payment=%s" % (self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][3], urllib.quote_plus(self.incomingMsisdn[msisdn][9]), urllib.quote_plus(self.incomingMsisdn[msisdn][9].split(",")[0]), urllib.quote_plus('Bang Joni, Palma One 2nd floor suit 210 Jakarta Selatan'), urllib.quote_plus(self.incomingMsisdn[msisdn][7]), urllib.quote_plus(EMAIL_NOTIF), self.incomingMsisdn[msisdn][5]))			
            print respAPI

            kodeBooking = ""
            kodePembayaran = ""
            batasPembayaran = ""
            pesan = ""
            url_pay = ""
            errormsg = ""

            sqlstart = respAPI.find("<kodeBooking>")
            sqlstop = respAPI.find("</kodeBooking>")
            if sqlstart != -1:
                kodeBooking = respAPI[sqlstart+13:sqlstop]

            sqlstart = respAPI.find("<kodePembayaran>")
            sqlstop = respAPI.find("</kodePembayaran>")
            if sqlstart != -1:
                kodePembayaran = respAPI[sqlstart+16:sqlstop]   

            sqlstart = respAPI.find("<batasPembayaran>")
            sqlstop = respAPI.find("</batasPembayaran>")
            if sqlstart != -1:            
               batasPembayaran = respAPI[sqlstart+17:sqlstop]

            sqlstart = respAPI.find("<pesan>")
            if sqlstart != -1:            
                sqlstop = respAPI.find("</pesan>")
                pesan = respAPI[sqlstart+7:sqlstop]  
				
            sqlstart = respAPI.find("<url_pay>")
            if sqlstart != -1:            
                sqlstop = respAPI.find("</url_pay>")
                url_pay = respAPI[sqlstart+9:sqlstop] 
            print url_pay 				

            sqlstart = respAPI.find("<ERROR>")
            if sqlstart != -1:            
                sqlstop = respAPI.find("</ERROR>")
                errormsg = respAPI[sqlstart+7:sqlstop]

            if len(kodeBooking) > 2:
                ask = "xt07aa"
                answer = self.doNlp(ask, msisdn, first_name)
                sql = "insert into booking_xtrans values('%s','%s','%s','%s')" % (msisdn, logDtm, kodeBooking, kodePembayaran)                                      
                print ">>", sql
                self.insert(sql)

                sql = "select * from searching_jadwal_xtrans where msisdn = '%s' and no = %s" % (msisdn, self.incomingMsisdn[msisdn][10])
                print sql
                sqlout = self.request(sql)
                harga = "0"
                for row in sqlout: 
                    print "--->", self.incomingMsisdn[msisdn][1], row[7]
                    x = int(row[7].replace(".","")) * int(self.incomingMsisdn[msisdn][1])
                    harga = '{0:,}'.format(x)
                    harga = harga.replace(",",".")

                if self.incomingMsisdn[msisdn][5] == "fin195":
                    self.sendMessageT2(msisdn, "Bang Joni sudah berhasil booking pesananmu, berikut detailnya:\nKode Booking: %s\nKode Pembayaran: %s\nJumlah Pembayaran: Rp. %s\nLakukan pembayaran via ATM secepatnya sebelum %s agar tiket kamu tidak dibatalkan.\nBang Joni akan kirim tiket jika pembayaran telah diterima." % (kodeBooking, kodePembayaran, harga, batasPembayaran), 0)
                    self.sendPhotoT2(msisdn, '/usr/share/nginx/html/line_images/tiketux_atm.jpg')
                elif self.incomingMsisdn[msisdn][5] == "indomaret":
                    self.sendMessageT2(msisdn, "Bang Joni sudah berhasil booking pesananmu, berikut detailnya:\nKode Booking: %s\nKode Pembayaran: %s\nJumlah Pembayaran: Rp. %s\nLakukan pembayaran ke Indomaret terdekat secepatnya sebelum %s agar tiket kamu tidak dibatalkan.\nBang Joni akan kirim tiket jika pembayaran telah diterima." % (kodeBooking, kodePembayaran, harga, batasPembayaran), 0)										
                else:
                    print "Bang Joni sudah berhasil booking pesananmu, berikut detailnya:\nKode Booking: %s\nKode Pembayaran: %s\nJumlah Pembayaran: Rp. %s\nLakukan pembayaran via %s dengan cara <a href=\"%s\">click disini</a> sebelum %s agar tiket kamu tidak dibatalkan.\nBang Joni akan kirim tiket jika pembayaran telah diterima." % (kodeBooking, kodePembayaran, harga, self.incomingMsisdn[msisdn][8], url_pay, batasPembayaran)
                    #self.sendMessageT2(msisdn, "Bang Joni sudah berhasil booking pesananmu, berikut detailnya:\nKode Booking: %s\nKode Pembayaran: %s\nJumlah Pembayaran: Rp. %s\nLakukan pembayaran via %s dengan cara <a href=\"%s\">click disini</a> sebelum %s agar tiket kamu tidak dibatalkan.\nBang Joni akan kirim tiket jika pembayaran telah diterima." % (kodeBooking, kodePembayaran, harga, self.incomingMsisdn[msisdn][8], url_pay, batasPembayaran), 0)
                    self.sendLinkMessageT2(msisdn, 'berhasil booking, detailnya:\nKode Booking: %s\nKode Pembayaran: %s\nHarga: Rp. %s\nLakukan pembayaran sebelum %s.\nBang Joni kirim tiket jika pembayaran diterima' % (kodeBooking, kodePembayaran, harga, batasPembayaran), self.incomingMsisdn[msisdn][8], 'Bayar Sekarang', url_pay, 'http://128.199.88.72/line_images/logobangjoni2.jpg')					
					
            if len(errormsg) > 2:
                self.sendMessageT2(msisdn, "Bang joni dapat info dari xtrans: %s" % (errormsg), 0)
                #self.sendMessageT2(msisdn, "Pilih kursi yang kosong aja ya..", 0)

            
####################XTRANS MODULE END####################

####################UBER MODULE START####################
        if answer[:4] == "ub01":
            self.log_service(logDtm, msisdn, first_name, "UBER")
            self.incomingMsisdn[msisdn][11] = "ub01"
            self.incomingMsisdn[msisdn][2] = -1
            sql = "select * from token_uber where msisdn = '%s'" % (msisdn)
            print sql
            sqlout = self.request(sql)
            token_uber = ""
            for row in sqlout:
                token_uber = row[2]
            if token_uber == "" or token_uber == "X":
                credentials = import_app_credentials()
                self.incomingMsisdn[msisdn][1] = AuthorizationCodeGrant(
                    credentials.get('client_id'),
                    credentials.get('scopes'),
                    credentials.get('client_secret'),
                    credentials.get('redirect_url'),
                )

                auth_url = self.incomingMsisdn[msisdn][1].get_authorization_url()
                state = auth_url.split('&')[1].split('=')[1]
                print ">>>>", auth_url, state
                self.insert("delete from token_uber where msisdn = '%s'" % (msisdn))
                sql = "insert into token_uber(msisdn, state, access_token, platform) values('" + msisdn + "','" + state + "','X','line')"
                self.insert(sql)  

                answer = "Bang Joni belum terhubung dengan account Ubermu\n"
                answer = answer + "Untuk memberikan ijin Bang Joni terhubung account Ubermu <a href=\"" + auth_url + "\">click disini</a> ya"
                #answer = answer + "Click url berikut untuk memberikan ijin BangJoni menggunakan uber accountmu:\n"
                #answer = answer + auth_url
                #self.sendMessageT2(msisdn, answer, 0)
                self.sendLinkMessageT2(msisdn, 'belum terhubung dengan account Ubermu\nUntuk memberikan ijin Bang Joni terhubung account Ubermu tap Ijin Uber', 'Uber', 'Ijin Uber', auth_url, 'http://128.199.88.72/line_images/uber.JPG')				
            else:
                answer = "Share lokasimu dengan cara click tombol PIN dan tap Location"
                self.sendMessageT2(msisdn, answer, 0)
        
        if ask[:5] == "[LOC]" and self.incomingMsisdn[msisdn][11] == "ub01":
            self.incomingMsisdn[msisdn][11] = "ub01"
            if self.incomingMsisdn[msisdn][2] == -1:
               self.incomingMsisdn[msisdn][2]  = ask[5:].split(';')[0]
               self.incomingMsisdn[msisdn][3]  = ask[5:].split(';')[1]
               self.sendMessageT2(msisdn, "Sekarang share lokasi tujuanmu dengan cara click tombol PIN dan tap Location", 0)
            elif self.incomingMsisdn[msisdn][2] != -1:
               self.incomingMsisdn[msisdn][4]  = ask[5:].split(';')[0]
               self.incomingMsisdn[msisdn][5]  = ask[5:].split(';')[1]
               answer = self.doNlp("ub02", msisdn, first_name)
               self.sendMessageT2(msisdn, answer, 0)
               print ">>>>", self.incomingMsisdn[msisdn]
               sql = "select * from token_uber where msisdn = '%s'" % (msisdn)
               print sql
               sqlout = self.request(sql)
               access_token = ""
               refresh_token = ""	
               for row in sqlout:
                   access_token = row[2]
                   refresh_token = row[1]	
               if access_token != "":
                   print "http://127.0.0.1/uber/request_ride.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&refresh_token=%s" % (self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][3], self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][5], access_token, refresh_token)
                   respAPI = self.fetchHTML("http://127.0.0.1/uber/request_ride.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&refresh_token=%s" % (self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][3], self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][5], access_token, refresh_token))   
                   print "REQUEST_RIDE:", respAPI
                   sqlstart = respAPI.find("access_token")
                   if sqlstart > -1:	
                       new_access_token = ""
                       new_refresh_token = ""
                       new_expires_in = ""					   
                       #sqlstart = respAPI.find("<new_access_token>")
                       #sqlstop = respAPI.find("</new_access_token>")
                       #new_access_token = respAPI[sqlstart+18:sqlstop]   
                       #sqlstart = respAPI.find("<new_refresh_token>")
                       #sqlstop = respAPI.find("</new_refresh_token>")
                       #new_refresh_token = respAPI[sqlstart+19:sqlstop]		
                       #sqlstart = respAPI.find("<new_expires_in>")
                       #sqlstop = respAPI.find("</new_expires_in>")
                       #new_expires_in = respAPI[sqlstart+16:sqlstop]							   
                       content = json.loads(respAPI)
                       print ">>>>>",content
                       new_access_token = content['access_token']		
                       new_refresh_token = content['refresh_token']				
                       new_expires_in = content['expires_in']		
                       access_token = new_access_token

                       sql = "update token_uber set access_token='%s', refresh_token='%s', expires_in_sec='%s' where msisdn='%s'" % (new_access_token, new_refresh_token, new_expires_in, msisdn)
                       print sql
                       self.insert(sql)  
					   
                       sql = "select * from token_uber where msisdn = '%s'" % (msisdn)
                       print sql
                       sqlout = self.request(sql)
                       email = ""
                       for row in sqlout:
                           email = row[6]
                       if email != "":
                           sql = "update token_uber set access_token='%s', refresh_token='%s', expires_in_sec='%s' where email='%s'" % (new_access_token, new_refresh_token, new_expires_in, email)
                           print sql
                           self.insert(sql)  					   
		
                       print "http://127.0.0.1/uber/request_ride.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&refresh_token=%s" % (self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][3], self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][5], new_access_token, new_refresh_token)
                       respAPI = self.fetchHTML("http://127.0.0.1/uber/request_ride.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&refresh_token=%s" % (self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][3], self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][5], new_access_token, new_refresh_token))   
                       print "REQUEST_RIDE_NEW_TOKEN:",respAPI	
					   
                   request_id = ""
                   status = ""
                   sqlstart = respAPI.find("<status>")
                   sqlstop = respAPI.find("</status>")
                   status = respAPI[sqlstart+8:sqlstop]   
                   sqlstart = respAPI.find("<request_id>")
                   sqlstop = respAPI.find("</request_id>")
                   request_id = respAPI[sqlstart+12:sqlstop]
   
                   if sqlstart > -1:
                       self.incomingMsisdn[msisdn][6] = request_id
                       self.incomingMsisdn[msisdn][7] = access_token
                       #self.insert("delete from booking_uber where msisdn = '%s'" % (msisdn))
                       sql = "insert into booking_uber values('" + msisdn + "','" + first_name + "','" + request_id + "','" + status + "','" + logDtm +  "','" + access_token + "','line')"
                       print sql
                       self.insert(sql)
                       self.incomingMsisdn[msisdn][11] = ""
                   else:
                       surge = ""
                       multiplier = ""
                       surge_confirmation_id = ""
                       request_id = "surge"

                       sqlstart = respAPI.find("<surge_confirmation_id>")
                       sqlstop = respAPI.find("</surge_confirmation_id>")
                       surge_confirmation_id = respAPI[sqlstart+23:sqlstop]   
                       sqlstart = respAPI.find("<multiplier>")
                       sqlstop = respAPI.find("</multiplier>")
                       multiplier = respAPI[sqlstart+12:sqlstop]   
                       sqlstart = respAPI.find("<surge>")
                       sqlstop = respAPI.find("</surge>")
                       surge = respAPI[sqlstart+7:sqlstop]
                       if sqlstart > -1:
                           sql = "insert into booking_uber values('" + msisdn + "','" + first_name + "','" + request_id + "','" + surge_confirmation_id + "','" + logDtm +  "','" + access_token + "','line')"
                           print sql
                           self.insert(sql)
                           answer = first_name + ", jam sekarang Uber lagi penuh, naik " + multiplier + " kali lipat tarif normal, jika tetep order, <a href=\"" + surge + "\">click disini</a>"
                           #answer = answer + surge
                           #self.sendMessageT2(msisdn, answer, 0)
                           self.sendLinkMessageT2(msisdn, "dapat info Uber jam sekarang lagi penuh, naik " + multiplier + " kali lipat tarif normal, jika tetep order", 'Uber', 'Tetap Pesan', surge, 'http://128.199.88.72/line_images/uber.JPG')					
                       else:
                           self.sendMessageT2(msisdn, "Bang Joni, nggak dapat response dari Uber, coba lagi ya...", 0)

####################TRAIN MODULE START####################
        if answer[:4] == "ke00":
            self.log_service(logDtm, msisdn, first_name, "TRAIN")
            self.incomingMsisdn[msisdn][11] = "ke00"
            print "*******************************>"

        if answer[:4] == "ke01":
            self.incomingMsisdn[msisdn][11] = "ke00"
            #calling kereta api API
            ask = "ke01"
            answer = self.doNlp(ask, msisdn, first_name)   
            self.sendMessageT2(msisdn, answer, 0)
            print "http://127.0.0.1/train/cari_train1.php?d=%s&a=%s&roundtrip=1&adult=%d&infant=%d&date=%s&ret_date=" % (self.incomingMsisdn[msisdn][3], self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][9], self.incomingMsisdn[msisdn][10], self.incomingMsisdn[msisdn][2])
            respAPI = self.fetchHTML("http://127.0.0.1/train/cari_train1.php?d=%s&a=%s&roundtrip=1&adult=%d&infant=%d&date=%s&ret_date=" % (self.incomingMsisdn[msisdn][3], self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][9], self.incomingMsisdn[msisdn][10], self.incomingMsisdn[msisdn][2]))

            sqlstart = respAPI.find("<TOKEN>")
            sqlstop = respAPI.find("</TOKEN>")
            token = respAPI[sqlstart+7:sqlstop]
                    

            sqlstart = respAPI.find("<SQL>")
            sqlstop = respAPI.find("</SQL>")
            list_airlines = respAPI[sqlstart+5:sqlstop]
 
            if list_airlines and len(token) == 40:   

                fo = open('/tmp/%s_cari.html' % (msisdn), "w")
                fo.write(respAPI)
                fo.close()
                options = {
                    'page-size': 'A6',
                    'margin-top': '0',
                    'margin-right': '0',
                    'margin-bottom': '0',
                    'margin-left': '0',
                    'encoding': "UTF-8"
                }
                try:
                    pdfkit.from_file('/tmp/%s_cari.html' % (msisdn), '/tmp/%s_cari.pdf' % (msisdn), options=options)
                except Exception as e:
                    print "Error pdfkit",e
                if os.path.exists('/tmp/%s_cari.pdf' % (msisdn)): 
                    outfile = '/tmp/%s_cari.pdf' % (msisdn)
                    pdf2jpg = PythonMagick.Image()
                    pdf2jpg.density("200")
                    pdf2jpg.read(outfile)
                    pdf2jpg.write("%s.jpg" % (outfile.split('.')[0]))  

                    #self.goHtml2Png(respAPI, msisdn)
                    print "Done convert html to pdf to png"                                                
                    #photo = open('%s.jpg' % (outfile.split('.')[0]), 'rb')
                    self.sendPhotoT2(msisdn, '%s.jpg' % (outfile.split('.')[0]))

                    self.incomingMsisdn[msisdn][13] = token                                          
                    self.insert("delete from searching_train where msisdn = '%s'" % (msisdn))
                    for item in list_airlines.split(';'):
                        sql = "insert into searching_train values('" + msisdn + "','" + self.incomingMsisdn[msisdn][2] + "',"
                        for sub_item in item.split('|'):
                            sql = sql + "'" + sub_item + "',"
                        if sub_item:
                            sql = sql + "'" + token + "')"   
                            print sql                                                     
                            self.insert(sql)  

            else:
                answer = "Bang Joni tidak menemukan kereta yang available. Coba tanggal atau rute lainnya."                    
                self.sendMessageT2(msisdn, answer, 0)
                self.incomingMsisdn[msisdn][14] = -1   
                self.incomingMsisdn[msisdn][15] = 2  

        if answer[:4] == "ke02":
            #calling kereta api API
            if self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] == 0:
                answer = "%d dewasa diatas 2 tahun dengan format: (Tn/Ny/Nona);nama lengkap;KTP" % (self.incomingMsisdn[msisdn][9])
            if self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] > 0:
                answer = "%d dewasa diatas 2 tahun dan %d bayi dengan format: (d=dewasa/b=bayi);(Tn/Ny/Nona);nama lengkap;KTP" % (self.incomingMsisdn[msisdn][9], self.incomingMsisdn[msisdn][10])
            self.sendMessageT2(msisdn, answer, 0)

        if answer[:4] == "ke04":
            #calling kereta api API
            ask = "ke04aa"
            print "AAAAAAAAAAAAAAAAAAAA"
            answer = self.doNlp(ask, msisdn, first_name)
            print "BBBBBBBBBBBBBBBBBBBB"
            print self.bookingMsisdn[msisdn]        
            self.incomingMsisdn[msisdn][14] = 1                    
            s = ""                    
            logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')   
            
            sql = "select * from searching_train where msisdn = '%s' and id = %s" % (msisdn, self.bookingMsisdn[msisdn]['train_id'])
            print sql
            sqlout = self.request(sql)
            departure_date = ""
            for row in sqlout:
                train_id = row[3]
                token = row[9]
                departure_date = row[1]
                subclass = row[4]
                dep_station = row[7]
                arr_station = row[6]
                train_name = row[5]
            if departure_date != "":
                 self.bookingMsisdn[msisdn]['d'] = dep_station
                 self.bookingMsisdn[msisdn]['a'] = arr_station
                 self.bookingMsisdn[msisdn]['date'] = departure_date
                 self.bookingMsisdn[msisdn]['token'] = token
                 self.bookingMsisdn[msisdn]['subclass'] = subclass
                 self.bookingMsisdn[msisdn]['train_id'] = train_id
            
                 for key in self.bookingMsisdn[msisdn]:
                     s = s + key + "=" + self.bookingMsisdn[msisdn][key] + "&"                                                              
                 self.bookingMsisdn[msisdn]['train_name'] = train_name 
                 s = s + "x=1"               
                 s = "http://127.0.0.1/train/order_wh_train.php?" + s    
                 print s
                 respAPI = self.fetchHTML(s)   
                 print ">>>>>>>>>>>>RESPONSE_ORDER_WH<<<<<<<<<<<<<"
                 print respAPI                    
                 if respAPI.find("order_succeed") >= 0:                                                                                                              

                    fo = open('/tmp/%s_order.html' % (msisdn), "w")
                    fo.write(respAPI)
                    fo.close()
                    options = {
                        'page-size': 'A6',
                        'margin-top': '0',
                        'margin-right': '0',
                        'margin-bottom': '0',
                        'margin-left': '0',
                        'encoding': "UTF-8"
                    }
                    try:
                        pdfkit.from_file('/tmp/%s_order.html' % (msisdn), '/tmp/%s_order.pdf' % (msisdn), options=options)
                    except Exception as e:
                        print "error pdfkit",e
                    if os.path.exists('/tmp/%s_order.pdf' % (msisdn)): 
                        outfile = '/tmp/%s_order.pdf' % (msisdn)
                        pdf2jpg = PythonMagick.Image()
                        pdf2jpg.density("200")
                        pdf2jpg.read(outfile)
                        pdf2jpg.write("%s.jpg" % (outfile.split('.')[0]))  

                        #self.goHtml2Png(respAPI, msisdn)
                        print "Done convert html to pdf to png"                                                
                        #photo = open('%s.jpg' % (outfile.split('.')[0]), 'rb')
                        self.sendPhotoT2(msisdn, '%s.jpg' % (outfile.split('.')[0]))
                         
                        sqlstart = respAPI.find("<TOKEN>")
                        sqlstop = respAPI.find("</TOKEN>")
                        token = respAPI[sqlstart+7:sqlstop]   
                        sqlstart = respAPI.find("<ORDERID>")
                        sqlstop = respAPI.find("</ORDERID>")
                        orderid = respAPI[sqlstart+9:sqlstop]    

                        
                         
                        sql = "insert into booking_train values('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (logDtm, msisdn, self.bookingMsisdn[msisdn]['date'], self.bookingMsisdn[msisdn]['train_id'], self.bookingMsisdn[msisdn]['train_name'], self.bookingMsisdn[msisdn]['a'], self.bookingMsisdn[msisdn]['d'], orderid, token )                                      
                        print ">>", sql
                        self.insert(sql)                                                
                        time.sleep(5)

                        s = "http://127.0.0.1/train/bayar_wh_train.php?token=%s&orderid=%s&title=%s&first_name=%s&email=%s&phone=%s" % (token, orderid, self.bookingMsisdn[msisdn]['conSalutation'], self.bookingMsisdn[msisdn]['conFirstName'], self.bookingMsisdn[msisdn]['conEmailAddress'], self.bookingMsisdn[msisdn]['conPhone'])                         
                        print s                         
                        respAPI = self.fetchHTML(s)  
                        if respAPI.find("ATM_SUKSES") >= 0:    
                            #self.goHtml2Png(respAPI, msisdn + "_bayar")
                            #print "Done convert html to png"    
                            del self.incomingMsisdn[msisdn]  
                            del self.bookingMsisdn[msisdn]                              
                            #self.sendImg("/tmp/%s_bayar.jpg" %(msisdn), msisdn)
                            print "Sukses ATM:"
                        else: 
                            print "Bayar error:", respAPI
                            answer = "Maaf, order pembayaran via ATM tdk bisa, ulangi lagi ya..."
                            err_msg = respAPI[respAPI.find("error_msgs")+10:respAPI.find("status")]   
                            err_msg = err_msg.translate(None, ",'!.?$%:\"")
                            #try:
                                #sql = "insert into booking_error values('%s','%s','%s','%s','%s')" % (logDtm, msisdn, self.incomingMsisdn[msisdn][13], s, err_msg)                                      
                                #self.insert(sql)  
                            #except:
                                #print "sql error at order gopegi"  
                            answer = answer + ": " + err_msg
                            self.sendMessageT2(msisdn, answer, 0)
                        try:
                            del self.incomingMsisdn[msisdn]  
                            del self.bookingMsisdn[msisdn]
                        except Exception as e:
                            return 1
####################TRAIN MODULE END####################

####################FLIGHT MODULE END####################
        if answer[:4] == "fl01":
            self.log_service(logDtm, msisdn, first_name, "FLIGHT")
            self.incomingMsisdn[msisdn][14] = 1
            self.incomingMsisdn[msisdn][15] = 2
                    
            print "http://127.0.0.1/flight/cari_whx_line.php?asal=%s&tujuan=%s&roundtrip=1&dewasa=%d&anak=%d&bayi=%d&pergi=%s&airline=%s&waktu=%s&transit=%s&pulang=" % (self.incomingMsisdn[msisdn][3], self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][9], self.incomingMsisdn[msisdn][10], self.incomingMsisdn[msisdn][11], self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][8], self.incomingMsisdn[msisdn][23], self.incomingMsisdn[msisdn][24])
            respAPI = self.fetchHTML("http://127.0.0.1/flight/cari_whx_line.php?asal=%s&tujuan=%s&roundtrip=1&dewasa=%d&anak=%d&bayi=%d&pergi=%s&airline=%s&waktu=%s&transit=%s&pulang=" % (self.incomingMsisdn[msisdn][3], self.incomingMsisdn[msisdn][4], self.incomingMsisdn[msisdn][9], self.incomingMsisdn[msisdn][10], self.incomingMsisdn[msisdn][11], self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][8], self.incomingMsisdn[msisdn][23], self.incomingMsisdn[msisdn][24]))
            print "----->", respAPI                      
            sqlstart = respAPI.find("<TOKEN>")
            sqlstop = respAPI.find("</TOKEN>")
            token = respAPI[sqlstart+7:sqlstop]
      

            sqlstart = respAPI.find("<SQL>")
            sqlstop = respAPI.find("</SQL>")
            list_airlines = respAPI[sqlstart+5:sqlstop]
            self.insert("insert into searched_tickets values ('" + logDtm + "','" + msisdn + "','" + self.incomingMsisdn[msisdn][3] + "','" + self.incomingMsisdn[msisdn][4] + "','" + self.incomingMsisdn[msisdn][8] + "','" + self.incomingMsisdn[msisdn][2] + "')")                        
            self.incomingMsisdn[msisdn][21] = self.incomingMsisdn[msisdn][3]                    
            self.incomingMsisdn[msisdn][22] = self.incomingMsisdn[msisdn][4]                    

            if list_airlines and len(token) == 40:  

                fo = open('/tmp/%s_cari.html' % (msisdn), "w")
                fo.write(respAPI)
                fo.close()
                options = {
                    'page-size': 'A6',
                    'margin-top': '0',
                    'margin-right': '0',
                    'margin-bottom': '0',
                    'margin-left': '0',
                    'encoding': "UTF-8"
                }
                try:
                    pdfkit.from_file('/tmp/%s_cari.html' % (msisdn), '/usr/share/nginx/html/line_images/%s_cari.pdf' % (msisdn), options=options)
                except Exception as e:
                    print "Error pdfkit",e
                if os.path.exists('/usr/share/nginx/html/line_images/%s_cari.pdf' % (msisdn)): 
                    #answer = "Berikut 9 penerbangan termurah sesuai kriteriamu.\nJika ada yang cocok sebut saja no pilihannya untuk Bang Joni booking.\nJika tidak ada yang cocok, Bang Joni bisa carikan jadwal lainnya."                    
                    ask = "fl01aa"
                    answer = self.doNlp(ask, msisdn, first_name)
                    #self.sendMessageT2(msisdn, answer, 0)

                    outfile = '/usr/share/nginx/html/line_images/%s_cari.pdf' % (msisdn)
                    pdf2jpg = PythonMagick.Image()
                    pdf2jpg.density("200")
                    pdf2jpg.read(outfile)
                    randomDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y%m%d%H%M%S')	
                    pdf2jpg.write("%s_%s.jpg" % (outfile.split('.')[0], randomDtm))  

                    #self.goHtml2Png(respAPI, msisdn)
                    print "Done convert html to pdf to png %s_%s.jpg" % (outfile.split('.')[0].split('/')[6], randomDtm)                                                
                    #photo = open('%s.jpg' % (outfile.split('.')[0]), 'rb')
                    #self.sendPhotoT2(msisdn, '%s.jpg' % (outfile.split('.')[0]))
                    self.sendPhotoCaptionT2(msisdn, 'http://128.199.88.72/line_images/%s_%s.jpg' % (outfile.split('.')[0].split('/')[6], randomDtm), 'http://128.199.88.72/line_images/%s_%s.jpg' % (outfile.split('.')[0].split('/')[6], randomDtm), answer)

					
                    self.incomingMsisdn[msisdn][13] = token                                          
                    self.insert("delete from searching_airlines where msisdn = '%s'" % (msisdn))
                    for item in list_airlines.split(';'):
                        sql = "insert into searching_airlines values('" + msisdn + "','" + self.incomingMsisdn[msisdn][2] + "',"
                        for sub_item in item.split('|'):
                            sql = sql + "'" + sub_item + "',"
                        if sub_item:
                            sql = sql + "'" + token + "')"   
                            print sql                                                     
                            self.insert(sql)                               
                   
                    self.incomingMsisdn[msisdn][14] = -1
                    list_airlines = ""                        
                                             
            else:
                answer = "Bang Joni tidak menemukan penerbangan. Sebut aja tanggal atau rute lainnya."                    
                self.sendMessageT2(msisdn, answer, 0)
                self.incomingMsisdn[msisdn][14] = -1   
                self.incomingMsisdn[msisdn][15] = 2  


        elif answer[:4] == "fl02":
            sql = "select * from searching_airlines where msisdn = '%s' and id = %s" % (msisdn, self.bookingMsisdn[msisdn]['flight_id'])
            print sql
            sqlout = self.request(sql)
            departure_date = ""
            for row in sqlout:
                flight_id = row[3]
                token = row[8]
                departure_date = row[1]
                flight_number = row[4]
                airlines_name = row[5]
                departure_time = row[6]
            if departure_date != "":
                web_request = "http://127.0.0.1/flight/form_wh.php?date=%s&ret_date=x&flight_id=%s&ret_flight_id=x&token=%s" % (departure_date, flight_id, token)
                self.bookingMsisdn[msisdn]['flight_id'] = flight_id
                self.bookingMsisdn[msisdn]['token'] = token  
                self.incomingMsisdn[msisdn][18] = flight_number    
                self.incomingMsisdn[msisdn][19] = airlines_name 
                self.incomingMsisdn[msisdn][20] = departure_time                                                                                         
                print web_request
                respAPI = self.fetchHTML(web_request)
                print respAPI
                if respAPI.find("<ADULT>") >= 0:
                    if respAPI.find("passportno") == -1:
                        if self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] == 0 and self.incomingMsisdn[msisdn][11] == 0:
                            answer = "Format penumpang untuk %s dewasa" % (self.incomingMsisdn[msisdn][9])
                            answer = answer + ", dg format: (Tn/Ny/Nona);nama lengkap;tgl lahir;"                                                         
                        elif self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] > 0 and self.incomingMsisdn[msisdn][11] == 0:
                            answer = "Format penumpang untuk %s dewasa %s anak" % (self.incomingMsisdn[msisdn][9], self.incomingMsisdn[msisdn][10])
                            answer = answer + ", dg format: (d=dewasa/a=anak);(Tn/Ny/Nona);nama lengkap;tgl lahir;"
                        elif self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] > 0 and self.incomingMsisdn[msisdn][11] > 0:    
                            answer = "Format penumpang untuk %s dewasa %s anak %s bayi" % (self.incomingMsisdn[msisdn][9], self.incomingMsisdn[msisdn][10], self.incomingMsisdn[msisdn][11])
                            answer = answer + ", dg format: (d=dewasa/a=anak/b=bayi);(Tn/Ny/Nona);nama lengkap;tgl lahir;"
                    else:
                        self.incomingMsisdn[msisdn][16] = 1
                        if self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] == 0 and self.incomingMsisdn[msisdn][11] == 0:
                            answer = "Format penumpang untuk %s dewasa" % (self.incomingMsisdn[msisdn][9])
                            answer = answer + ", dg format: (Tn/Ny/Nona);nama lengkap;tgl lahir;no paspor;negara penerbit paspor;tgl terbit paspor;tgl expired paspor;"                         
                        elif self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] > 0 and self.incomingMsisdn[msisdn][11] == 0:
                            answer = "Format penumpang untuk %s dewasa %s anak" % (self.incomingMsisdn[msisdn][9], self.incomingMsisdn[msisdn][10])
                            answer = answer + ", dg format: (d=dewasa/a=anak);(Tn/Ny/Nona);nama lengkap;tgl lahir;no paspor;negara penerbit paspor;tgl terbit paspor;tgl expired paspor;"
                        elif self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] > 0 and self.incomingMsisdn[msisdn][11] > 0:    
                            answer = "Format penumpang untuk %s dewasa %s anak %s bayi" % (self.incomingMsisdn[msisdn][9], self.incomingMsisdn[msisdn][10], self.incomingMsisdn[msisdn][11])
                            answer = answer + ", dg format: (d=dewasa/a=anak/b=bayi);(Tn/Ny/Nona);nama lengkap;tgl lahir;no paspor;negara penerbit paspor;tgl terbit paspor;tgl expired paspor;"                                                   
                        
                    if respAPI.find("dcheckinbaggagea") != -1:
                        answer = answer + "(0,15,20,25,30,35,40)kg;"
                        self.incomingMsisdn[msisdn][17] = 1
                            
                    if respAPI.find("passportno") == -1 and respAPI.find("dcheckinbaggagea") == -1:
                        if self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] == 0 and self.incomingMsisdn[msisdn][11] == 0:
                            answer = answer + "\n" + "Contoh: Tn;kenzie abinaya;5mei1980;"  
                        elif self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] > 0 and self.incomingMsisdn[msisdn][11] == 0:
                            answer = answer + "\n" + "Contoh: d;Tn;kenzie abinaya;5mei1980;" + "\n" + "a;Nona;keke abinaya;5mei2008;"  
                        elif self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] > 0 and self.incomingMsisdn[msisdn][11] > 0:    
                            answer = answer + "\n" + "Contoh: d;Tn;kenzie abinaya;5mei1980;" + "\n" + "a;Nona;keke abinaya;5mei2008;" + "\n" + "b;Nona;kia abinaya;5mei2014;"
                                   
                    if respAPI.find("passportno") == -1 and respAPI.find("dcheckinbaggagea") != -1:
                        if self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] == 0 and self.incomingMsisdn[msisdn][11] == 0:
                            answer = answer + "\n" + "Contoh: Tn;kenzie abinaya;5mei1980;15;"  
                        elif self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] > 0 and self.incomingMsisdn[msisdn][11] == 0:
                            answer = answer + "\n" + "Contoh: d;Tn;kenzie abinaya;5mei1980;15;" + "\n" + "a;Nona;keke abinaya;5mei2008;0;"  
                        elif self.incomingMsisdn[msisdn][9] > 0 and self.incomingMsisdn[msisdn][10] > 0 and self.incomingMsisdn[msisdn][11] > 0:    
                            answer = answer + "\n" + "Contoh: d;Tn;kenzie abinaya;5mei1980;15;" + "\n" + "a;Nona;keke abinaya;5mei2008;0;" + "\n" + "b;Nona;kia abinaya;5mei2014;0;"                                    
                         
                    self.incomingMsisdn[msisdn][15] = 3
                else:
                    answer = "Maaf, terjadi kesalahan, mohon coba lagi"
                    self.incomingMsisdn[msisdn] = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""]
                self.sendMessageT2(msisdn, answer, 0)
                    
         
        elif answer[:4] == "fl06":
            ask = "fl04aa"
            print "AAAAAAAAAAAAAAAAAAAA"
            answer = self.doNlp(ask, msisdn, first_name)
            print "BBBBBBBBBBBBBBBBBBBB"
            print self.bookingMsisdn[msisdn]        
            self.incomingMsisdn[msisdn][14] = 1                    
            s = ""                    
            logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')   
            for key in self.bookingMsisdn[msisdn]:
                s = s + key + "=" + self.bookingMsisdn[msisdn][key] + "&"                                                              
            s = s + "paymentmethod=" + urllib.quote_plus(self.incomingMsisdn[msisdn][16])               
            s = "http://127.0.0.1/flight/order_wh1.php?" + s    
            print s
            respAPI = self.fetchHTML(s)   
            print ">>>>>>>>>>>>RESPONSE_ORDER_WH<<<<<<<<<<<<<"
            print respAPI                    
            if respAPI.find("book_succeded_proceed_to_available_payment") >= 0:                                                                                                              

                fo = open('/tmp/%s_order.html' % (msisdn), "w")
                fo.write(respAPI)
                fo.close()
                options = {
                    'page-size': 'A6',
                    'margin-top': '0',
                    'margin-right': '0',
                    'margin-bottom': '0',
                    'margin-left': '0',
                    'encoding': "UTF-8"
                }
                try:
                    pdfkit.from_file('/tmp/%s_order.html' % (msisdn), '/usr/share/nginx/html/line_images/%s_order.pdf' % (msisdn), options=options)
                except Exception as e:
                    print "error pdfkit",e
                if os.path.exists('/usr/share/nginx/html/line_images/%s_order.pdf' % (msisdn)): 
                    outfile = '/usr/share/nginx/html/line_images/%s_order.pdf' % (msisdn)
                    pdf2jpg = PythonMagick.Image()
                    pdf2jpg.density("200")
                    pdf2jpg.read(outfile)
                    randomDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y%m%d%H%M%S')
                    pdf2jpg.write("%s_%s.jpg" % (outfile.split('.')[0], randomDtm))  

                    #self.goHtml2Png(respAPI, msisdn)
                    print "Done convert html to pdf to png"                                                
                    #photo = open('%s.jpg' % (outfile.split('.')[0]), 'rb')
                    self.sendPhotoT2(msisdn, '%s_%s.jpg' % (outfile.split('.')[0], randomDtm))
                         
                    sqlstart = respAPI.find("<TOKEN>")
                    sqlstop = respAPI.find("</TOKEN>")
                    token = respAPI[sqlstart+7:sqlstop]   
                    sqlstart = respAPI.find("<ORDERID>")
                    sqlstop = respAPI.find("</ORDERID>")
                    orderid = respAPI[sqlstart+9:sqlstop]                                                    
                    sqlstart = respAPI.find("<URL_PAYMENT>")
                    sqlstop = respAPI.find("</URL_PAYMENT>")
                    url_payment = respAPI[sqlstart+13:sqlstop]   

                    sql = "insert into booking_tickets values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (logDtm, msisdn, self.incomingMsisdn[msisdn][21], self.incomingMsisdn[msisdn][22], self.incomingMsisdn[msisdn][2], self.incomingMsisdn[msisdn][20], self.incomingMsisdn[msisdn][18], self.incomingMsisdn[msisdn][19], orderid, token, s)                                      
                    self.insert(sql)                                                
                    time.sleep(3)

                    if self.incomingMsisdn[msisdn][16] == "ATM Transfer":
					    #s = "http://127.0.0.1/bayar_wh.php?s=https://api.tiket.com/checkout/checkout_payment/35&token=" + self.incomingMsisdn[msisdn][13]                        
                        s = "http://127.0.0.1/flight/bayar_wh.php?s=%s&token=%s" % (url_payment, self.incomingMsisdn[msisdn][13])
                        print s                         
                        respAPI = self.fetchHTML(s)  
                        if respAPI.find("Ringkasan Pembayaran") >= 0:    
                            #self.goHtml2Png(respAPI, msisdn + "_bayar")
                            #print "Done convert html to png"    
                            del self.incomingMsisdn[msisdn]  
                            del self.bookingMsisdn[msisdn]                              
                            #self.sendImg("/tmp/%s_bayar.jpg" %(msisdn), msisdn)
                            print "Sukses ATM:"
                        else: 
                            #print "Bayar error:", respAPI
                            answer = "Maaf, order pembayaran via ATM tdk bisa, ulangi lagi ya..."
                            print answer
                            err_msg = respAPI[respAPI.find("error_msgs")+10:respAPI.find("status")]   
                            err_msg = err_msg.translate(None, ",'!.?$%:\"")
                            try:
                                sql = "insert into booking_error values('%s','%s','%s','%s','%s')" % (logDtm, msisdn, self.incomingMsisdn[msisdn][13], s, err_msg)                                      
                                self.insert(sql)  
                            except:
                                print "sql error at order gopegi"  
                            answer = answer + ": " + err_msg
                            self.sendMessageT2(msisdn, answer, 0)
                            del self.incomingMsisdn[msisdn]  
                            del self.bookingMsisdn[msisdn]
                    elif self.incomingMsisdn[msisdn][16] == "Credit Card" or self.incomingMsisdn[msisdn][16] == "CIMB Clicks" or self.incomingMsisdn[msisdn][16] == "BCA KlikPay":
                        url = "https://tiket.com/payment/checkout_payment?currency=IDR&token=%s&checkouttoken=%s&payment_type=%s" % (token, token, url_payment.split("=")[1])
                        print "Tiketdotcom_payment:", url
                        #self.sendMessageT2(msisdn, "Bang Joni berhasil booking tiketmu.\nUntuk melakukan pembayaran via %s <a href=\"%s\">click disini</a>.\nBang Joni segera kirim tiket setelah pembayaran." % (self.incomingMsisdn[msisdn][16], url), 0)
                        self.sendLinkMessageT2(msisdn, 'berhasil booking, segera lakukan pembayaran via %s.\nBang Joni segera kirim tiket setelah pembayaran diterima' % (self.incomingMsisdn[msisdn][16]), self.incomingMsisdn[msisdn][16], 'Bayar Sekarang', url, 'http://128.199.88.72/line_images/logobangjoni2.jpg')						
                    else:
                        url = "https://api.tiket.com/payment/checkout_payment?currency=IDR&token=%s&checkouttoken=%s&payment_type=%s" % (token, token, url_payment.split("=")[1])
                        print "Tiketdotcom_payment:", url
                        #self.sendMessageT2(msisdn, "Bang Joni berhasil booking tiketmu.\nUntuk melakukan pembayaran via %s <a href=\"%s\">click disini</a>.\nBang Joni segera kirim tiket setelah pembayaran." % (self.incomingMsisdn[msisdn][16], url), 0)
                        self.sendLinkMessageT2(msisdn, ' berhasil booking, segera lakukan pembayaran via %s.\nBang Joni segera kirim tiket setelah pembayaran diterima' % (self.incomingMsisdn[msisdn][16]), self.incomingMsisdn[msisdn][16], 'Bayar Sekarang', url, 'http://128.199.88.72/line_images/logobangjoni2.jpg')						

            else: 
                print "Order error:", respAPI
                if respAPI.find("Error Ticket Booking step add flight:") >= 0: 
                    answer = "Maaf, booking tidak bisa, ulangi lagi ya..."
                    err_msg = respAPI[respAPI.find("error_msgs")+10:respAPI.find("status")] 
                elif respAPI.find("Error Ticket Booking step order:") >= 0: 
                    answer = "Maaf, order tidak bisa, ulangi lagi ya..."
                    err_msg = respAPI[respAPI.find("error_msgs")+10:respAPI.find("status")] 
                elif respAPI.find("Error Ticket Booking step order checkout:") >= 0: 
                    answer = "Maaf, order checkout tidak bisa, ulangi lagi ya..."
                    err_msg = respAPI[respAPI.find("error_msgs")+10:respAPI.find("status")] 
                elif respAPI.find("Error Ticket Booking step checkout customer") >= 0: 
                    answer = "Maaf, customer checkout tidak bisa, ulangi lagi ya..."
                    err_msg = respAPI[respAPI.find("error_msgs")+10:respAPI.find("status")] 
                elif respAPI.find("Error Ticket Booking step checkout payment:") >= 0: 
                    answer = "Maaf, payment checkout tidak bisa, ulangi lagi ya..."
                    err_msg = respAPI[respAPI.find("error_msgs")+10:respAPI.find("status")] 
                else:
                    answer = "Maaf, pemesanan tidak bisa, ulangi lagi ya"
                    err_msg = "CURL error"
                err_msg = err_msg.translate(None, ",'!.?$%:\"")
                try:
                    sql = "insert into booking_error values('%s','%s','%s','%s','%s')" % (logDtm, msisdn, self.incomingMsisdn[msisdn][13], s, err_msg)                                      
                    print sql
                    self.insert(sql)  
                except:
                    print "sql error at order gopegi"
                answer = answer + ": " + err_msg
                self.sendMessageT2(msisdn, answer, 0)
                del self.incomingMsisdn[msisdn]  
                del self.bookingMsisdn[msisdn] 
        #elif answer.find("Maaf") >= 0:
            #pass

####################LOG MESSAGES####################
        sql = "insert into asking_request values('" + logDtm + "','" + msisdn + "','" + first_name + "','" + ask + "')"
        print sql
        #thread.start_new_thread(stack.insert, (sql,))
        sql = "insert into asking_response values('" + logDtm + "','" + msisdn + "','" + first_name + "','" + answer + "')"
        print sql
        #thread.start_new_thread(self.insert, (sql,))        
#################################################

    def uber_request_ride_surge(self, surge_confirmation_id):
        logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        sql = "select * from booking_uber where status = '%s'" % (surge_confirmation_id)
        print sql
        sqlout = self.request(sql)
        access_token = ""
        msisdn_uber = ""
        first_name = ""
        for row in sqlout:
            msisdn_uber = row[0]
            access_token = row[5]
            first_name = row[1]
        if access_token != "" and self.incomingMsisdn[msisdn_uber][2] != -1 and self.incomingMsisdn[msisdn_uber][3] != -1:
            print "http://127.0.0.1/uber/request_ride_surge.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&surge_id=%s" % (self.incomingMsisdn[msisdn_uber][2], self.incomingMsisdn[msisdn_uber][3], self.incomingMsisdn[msisdn_uber][4], self.incomingMsisdn[msisdn_uber][5], access_token, surge_confirmation_id)
            respAPI = self.fetchHTML("http://127.0.0.1/uber/request_ride_surge.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&surge_id=%s" % (self.incomingMsisdn[msisdn_uber][2], self.incomingMsisdn[msisdn_uber][3], self.incomingMsisdn[msisdn_uber][4], self.incomingMsisdn[msisdn_uber][5], access_token, surge_confirmation_id))   
            print respAPI 
            request_id = ""
            status = ""
            sqlstart = respAPI.find("<status>")
            sqlstop = respAPI.find("</status>")
            status = respAPI[sqlstart+8:sqlstop]   
            sqlstart = respAPI.find("<request_id>")
            sqlstop = respAPI.find("</request_id>")
            request_id = respAPI[sqlstart+12:sqlstop]
   
            if sqlstart > -1:
                self.sendMessageT2(msisdn_uber, "Ok, Bang Joni order Uber dengan tarif peak...", 0)
                self.incomingMsisdn[msisdn_uber][6] = request_id
                self.incomingMsisdn[msisdn_uber][7] = access_token
                #self.insert("delete from booking_uber where msisdn = '%s'" % (msisdn))
                sql = "insert into booking_uber values('" + msisdn_uber + "','" + first_name + "','" + request_id + "','" + status + "','" + logDtm +  "','" + access_token + "','line')"
                print sql
                self.insert(sql)
                self.incomingMsisdn[msisdn_uber][11] = ""
            else:
                self.sendMessageT2(msisdn_uber, "Bang Joni, nggak dapat response dari Uber, coba lagi ya...", 0)


    def uber_send_notification(self, event_id, event_time, event_type, meta_user_id, meta_resource_id, meta_resource_type, meta_status, resource_href):
        sql = "select * from booking_uber where request_id = '%s'" % (meta_resource_id)
        print sql
        sqlout = self.request(sql)
        msisdn_uber = ""
        for row in sqlout:
            msisdn_uber = row[0]
            first_name = row[1]
            access_token = row[5]
        if msisdn_uber != "":
            sql = "update booking_uber set status = '%s' where msisdn = '%s' and request_id = '%s'" % (meta_status, msisdn_uber, meta_resource_id)
            print sql
            stack.insert(sql)
            if meta_status == "accepted":
                print "http://127.0.0.1/uber/get_notified.php?status=accepted&access_token=%s&resourcehref=%s" % (access_token, urllib.quote_plus(resource_href))
                respAPI = self.fetchHTML("http://127.0.0.1/uber/get_notified.php?status=accepted&access_token=%s&resourcehref=%s" % (access_token, urllib.quote_plus(resource_href)))   
                print respAPI 
                driver_phone = ""
                driver_rating = ""
                driver_name = ""
                vehicle_make = ""
                vehicle_model = ""
                license_plate = ""
                driver_picture = ""
                vehicle_picture = ""
                eta = ""

                sqlstart = respAPI.find("<driver_phone>")
                sqlstop = respAPI.find("</driver_phone>")
                driver_phone = respAPI[sqlstart+14:sqlstop]  
                sqlstart = respAPI.find("<driver_rating>")
                sqlstop = respAPI.find("</driver_rating>")
                driver_rating = respAPI[sqlstart+15:sqlstop]  
                sqlstart = respAPI.find("<vehicle_make>")
                sqlstop = respAPI.find("</vehicle_make>")
                vehicle_make = respAPI[sqlstart+14:sqlstop]
                sqlstart = respAPI.find("<vehicle_model>")
                sqlstop = respAPI.find("</vehicle_model>")
                vehicle_model = respAPI[sqlstart+15:sqlstop]  
                sqlstart = respAPI.find("<license_plate>")
                sqlstop = respAPI.find("</license_plate>")
                license_plate = respAPI[sqlstart+15:sqlstop]   
                sqlstart = respAPI.find("<eta>")
                sqlstop = respAPI.find("</eta>")
                eta = respAPI[sqlstart+5:sqlstop]  

                sqlstart = respAPI.find("<driver_picture>")
                sqlstop = respAPI.find("</driver_picture>")
                driver_picture = respAPI[sqlstart+16:sqlstop]  
                sqlstart = respAPI.find("<vehicle_picture>")
                sqlstop = respAPI.find("</vehicle_picture>")
                vehicle_picture = respAPI[sqlstart+17:sqlstop]   

                sqlstart = respAPI.find("<driver_name>")
                sqlstop = respAPI.find("</driver_name>")
                driver_name = respAPI[sqlstart+13:sqlstop]
                if sqlstart > -1:
                    answer = "Bang Joni sudah mendapatkan mobil buatmu, estimasi kedatangan " + eta + " menit, berikut data driver-nya:"
                    #self.sendMessageT2(msisdn_uber, answer, 0)
                    f = open('/usr/share/nginx/html/line_images/' + driver_picture.split('/')[-1],'wb')
                    f.write(urllib.urlopen(driver_picture).read())
                    f.close()
                    answer = "Driver: " + driver_name + "\nHP: " + driver_phone + "\nRating: " + driver_rating + "\nMobil: " + vehicle_make + " " + vehicle_model + "\nNopol: " + license_plate
                    #self.sendPhotoT2(msisdn_uber, '/tmp/' + driver_picture.split('/')[-1], answer)
                    self.sendPhotoCaptionT2(msisdn_uber, 'http://128.199.88.72/line_images/%s' % (driver_picture.split('/')[-1]), 'http://128.199.88.72/line_images/%s' % (driver_picture.split('/')[-1]), answer)
					
                    #f = open('/tmp/' + vehicle_picture.split('/')[-1],'wb')
                    #f.write(urllib.urlopen(vehicle_picture).read())
                    #f.close()
                    #answer = vehicle_model + ", Nopol " + license_plate
                    #self.sendPhotoT2(msisdn_uber, '/tmp/' + vehicle_picture.split('/')[-1], answer)
                    
                    
            if meta_status == "ready":
                print "http://127.0.0.1/uber/receipt_ride.php?access_token=%s&request_id=%s" % (access_token, meta_resource_id)
                respAPI = self.fetchHTML("http://127.0.0.1/uber/receipt_ride.php?access_token=%s&request_id=%s" % (access_token, meta_resource_id))   
                print respAPI 
                total_charged = ""
                duration = ""
                distance = ""
                distance_label = ""
                currency_code = ""

                sqlstart = respAPI.find("<duration>")
                sqlstop = respAPI.find("</duration>")
                duration = respAPI[sqlstart+10:sqlstop]   
                sqlstart = respAPI.find("<distance>")
                sqlstop = respAPI.find("</distance>")
                distance = respAPI[sqlstart+10:sqlstop]
                sqlstart = respAPI.find("<distance_label>")
                sqlstop = respAPI.find("</distance_label>")
                distance_label = respAPI[sqlstart+16:sqlstop]  
                sqlstart = respAPI.find("<currency_code>")
                sqlstop = respAPI.find("</currency_code>")
                currency_code = respAPI[sqlstart+15:sqlstop]   
                sqlstart = respAPI.find("<total_charged>")
                sqlstop = respAPI.find("</total_charged>")
                total_charged = respAPI[sqlstart+15:sqlstop]
                if sqlstart > -1:
                    #answer = first_name + ", total charge Uber %s %s, dengan jarak %s %s dan lama kamu perjalanan %s" % (currency_code, total_charged, distance, distance_label, duration)
                    answer = first_name + ", total charge Uber kamu %s, dengan jarak %s %s dan lama perjalanan kamu %s" % (total_charged, distance, distance_label, duration)
                    self.sendMessageT2(msisdn_uber, answer, 0)
                else:
                    self.sendMessageT2(msisdn_uber, "Info charge, Bang Joni nggak dapat dari Uber", 0)

            if meta_status == "arriving":
                answer = "Mobilmu sudah mau sampe, siap-siap..."
                self.sendMessageT2(msisdn_uber, answer, 0)

            if meta_status == "in_progress":
                answer = "Safe trip ya, pangggil bang Joni lagi klo butuh uber"
                self.sendMessageT2(msisdn_uber, answer, 0)
                answer = self.doNlp("exittorandom", msisdn_uber, first_name)
                try:
                    del self.incomingMsisdn[msisdn_uber]  
                    del self.bookingMsisdn[msisdn_uber]
                except:
                    print "Error cancel order"

            if meta_status == "no_drivers_available":  
                answer = "Bang Joni nggak nemu driver, kemungkinan lagi penuh.\nCoba lagi ntar ya.."
                self.sendMessageT2(msisdn_uber, answer, 0)
                answer = self.doNlp("exittorandom", msisdn_uber, first_name)

            if meta_status == "driver_canceled": 
                answer = "Driver-nya batalin pesenanmu.\nCoba lagi ntar ya.."
                self.sendMessageT2(msisdn_uber, answer, 0)
                answer = self.doNlp("exittorandom", msisdn_uber, first_name)
				
            if meta_status == "completed": 
                answer = "Bang Joni dapat pesen dari Uber: Terima Kasih telah memilih Uber dan sampai ketemu di perjalanan yg akan datang"
                self.sendMessageT2(msisdn_uber, answer, 0)
                answer = self.doNlp("exittorandom", msisdn_uber, first_name)				

    @idlerInit("email received")
    def onEmailReceived(self, filename, filetype):
        logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        print("%s email received %s" % (logDtm, filename))  
        state = 0
        
        if filetype == "pdf":   
            sql = "select * from booking_tickets where order_id = '%s'" % (filename.split(':')[0])
            print sql
            sqlout = self.request(sql)
            msisdn = "";
            for row in sqlout:
                msisdn = row[1]

            if msisdn == "":
                sql = "select * from booking_xtrans where kodebooking = '%s'" % (filename.split(':')[1].split('.')[0])
                print sql
                sqlout = self.request(sql)
                msisdn = "";
                for row in sqlout:
                    msisdn = row[0]

            if msisdn != "":
                pdffilename = filename.split(':')[1]
                pdf_im = PyPDF2.PdfFileReader(file("/tmp/%s" % (pdffilename), "rb"))
                npage = pdf_im.getNumPages()
                print("Converting %d pages" % npage)
                for p in range(npage):
                    pdf2jpg = PythonMagick.Image()
                    pdf2jpg.density("200")
                    pdf2jpg.read("/tmp/%s[%d]" % (pdffilename, p))
                    pdf2jpg.write("/usr/share/nginx/html/line_images/%sP%d.jpg" % (pdffilename.split('.')[0], p))
                    print("%s send attachment %s page %d to %s" % (logDtm, filename, p, msisdn))
                    #photo = open('/tmp/%sP%d.jpg' % (pdffilename.split('.')[0], p), 'rb')
                    self.sendPhotoT2(msisdn, '/usr/share/nginx/html/line_images/%sP%d.jpg' % (pdffilename.split('.')[0], p))
                    #self.sendMessageT2("139934550", "TEST", 0)
        
        elif filetype == "html":
            sql = "select * from booking_tickets where order_id = '%s'" % (filename.split('.')[0])
            print sql
            sqlout = self.request(sql)
            msisdn = "";
            for row in sqlout:
                msisdn = row[1]
            
            if msisdn != "":
                outfile = msisdn + "_order_" + filename + ".pdf"
                options = {
                    'page-size': 'A3'
                } 
                try:           
                   pdfkit.from_file('/tmp/%s' % (filename), '/usr/share/nginx/html/line_images/%s' % (outfile), options=options)
                except Exception as e:
                  print "error", e
                if os.path.exists('/usr/share/nginx/html/line_images/%s' % (outfile)):    
                   pdf2jpg = PythonMagick.Image()
                   pdf2jpg.density("200")
                   pdf2jpg.read("/usr/share/nginx/html/line_images/%s" % (outfile))
                   pdf2jpg.write("/usr/share/nginx/html/line_images/%s.jpg" % (outfile.split('.')[0]))                              
                   print("%s send attachment %s" % (logDtm, outfile))                                                                 
                   #self.sendImg("/tmp/%s.jpg" % (outfile.split('.')[0]), msisdn)
                   self.sendMessageT2(msisdn, "Tiket pesawat kamu sudah Bang Joni booking.\nSilakan lakukan transaksi pembayaran tiket pesawat kamu via ATM. \nTiket otomatis dikirim jika pembayaran telah diterima, maks 60 menit.", 0)  
        
        else:
            sql = "select * from booking_tickets where order_id = '%s'" % (filename.split('.')[0])
            print sql
            sqlout = self.request(sql)
            msisdn = "";
            for row in sqlout:
                msisdn = row[1]

            if msisdn == "":    
                state = 1
                sql = "select * from booking_train where order_id = '%s'" % (filename.split('.')[0])
                print sql
                sqlout = self.request(sql)
                msisdn = "";
                for row in sqlout:
                    msisdn = row[1]

            if msisdn == "":
                state = 2
                sql = "select * from booking_xtrans where kodebooking = '%s'" % (filename.split('.')[1])
                print sql
                sqlout = self.request(sql)
                msisdn = "";
                for row in sqlout:
                    msisdn = row[0]

            if msisdn != "":                       
                self.sendMessageT2(msisdn, filetype)
                #if state == 2:
                    #photo = open('/tmp/tiketux_atm.png', 'rb')
                    #bot.send_photo(msisdn, photo)
                
                #Artajasa payment info for tiket.com
                if filetype.find("Artajasa") >= 0:  
                    #photo = open('/home/ubuntu/telegram/images/artajasa_payment.png', 'rb')
                    self.sendPhotoT2(msisdn, 'images/artajasa_payment.png')
        return 1





def init_qtgui(display=None, style=None, qtargs=None):
    """Initiates the QApplication environment using the given args."""
    if QApplication.instance():
        print "0"
        logger.debug("QApplication has already been instantiated. \
                        Ignoring given arguments and returning existing QApplication.")
        return QApplication.instance()

    qtargs2 = [sys.argv[0]]
    if display:
        qtargs2.append('-display')
        qtargs2.append(display)
        # Also export DISPLAY var as this may be used
        # by flash plugin
        os.environ["DISPLAY"] = display

    if style:
        qtargs2.append('-style')
        qtargs2.append(style)

    qtargs2.extend(qtargs or [])
    return QApplication(qtargs2)

#139934550 xiaomi
#133310095 alpha

def list_contents(msisdn, ask, longitude, latitude, username, first_name, last_name, phone_number, first_name_c, last_name_c):
    print "Incoming>>>", msisdn, ask, longitude, latitude, username, first_name
    if incomingClient.has_key(msisdn) or ask[:1] == "/":
        print "thread exist for:", msisdn
    else:
        print "thread created for:", msisdn
        incomingClient[msisdn] = 1
        if longitude != "":
            ask = "[LOC]" + str(latitude) + ";" + str(longitude)
            print ">>>>>>>", longitude, ask
        thread.start_new_thread(handler, (msisdn, ask, first_name))

def list_contents2(msisdn, ask, longitude, latitude, username, first_name, last_name, phone_number, first_name_c, last_name_c):
    logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
    #do_stuff(ask)    
    #if msisdn == "139934550": print "Incoming>>>", logDtm, first_name, msisdn, ask, longitude, latitude, username
    print "Incoming>>>", logDtm, first_name, msisdn, ask, longitude, latitude, username
    if uniqClient.has_key(msisdn):
        pass
    else:
        uniqClient[msisdn] = 1
    if incomingClient.has_key(msisdn):
        if msisdn == "139934550": print "thread exist for:", msisdn
    else:
        if ask[:6] == "/start": ask = "start"
        if msisdn == "139934550": print "thread created for:", msisdn
        incomingClient[msisdn] = 1
        if longitude != "":
            ask = "[LOC]" + str(latitude) + ";" + str(longitude)
            print ">>>>>>>", longitude, ask
        displayname = stack.get_line_username(msisdn)
        handler(logDtm, msisdn, ask, displayname)

def do_stuff(s):
    if str(s) == "Loadx":
        print "load start"
        time.sleep(10)
        print "load ended"

def uber_authorization(msisdn, code):
    print "uber_authorization >>>>>", msisdn, code
    sql = "select * from token_uber where state = '%s'" % (msisdn)
    print sql
    sqlout = stack.request(sql)
    msisdn_uber = ""
    platform = ""
    email = ""
    for row in sqlout:
        msisdn_uber = row[0]
        platform = row[5]

    
    if msisdn_uber != "":
        #result_redirect = "http://127.0.0.1/uber_token?state=%s&code=%s" % (msisdn, code)
        result_redirect = "http://128.199.88.72:8443/uber_token?state=%s&code=%s" % (msisdn, code)
        print ">>>", result_redirect
        try:
            session = stack.incomingMsisdn[msisdn_uber][1].get_session(result_redirect)

        except (ClientError, UberIllegalState), error:
            print ">>>", error
            return

        credential = session.oauth2credential

        credential_data = {
            'client_id': credential.client_id,
            'redirect_url': credential.redirect_url,
            'access_token': credential.access_token,
            'expires_in_seconds': credential.expires_in_seconds,
            'scopes': list(credential.scopes),
            'grant_type': credential.grant_type,
            'client_secret': credential.client_secret,
            'refresh_token': credential.refresh_token,
        }
        print "1>>>>", credential.access_token, credential.refresh_token, credential.expires_in_seconds
		
        myUber = UberRidesClient(session, sandbox_mode=False)
        try:
            response = myUber.get_user_profile()
            profile = response.json
            first_name = profile.get('first_name')
            email = profile.get('email')
            print ">>>>", first_name, email			
        except (ClientError, ServerError), error:
            print ">>>", error
            return
			
        sql = "update token_uber set access_token='%s', refresh_token='%s', expires_in_sec='%s', email='%s' where msisdn='%s'" % (credential.access_token, credential.refresh_token, credential.expires_in_seconds, email, msisdn_uber)
        print sql
        stack.insert(sql)  
        sql = "update token_uber set access_token='%s', refresh_token='%s', expires_in_sec='%s', email='%s' where email='%s'" % (credential.access_token, credential.refresh_token, credential.expires_in_seconds, email, email)
        print sql
        stack.insert(sql)  			
        stack.sendMessageT2(msisdn_uber, "Account ubermu sudah terhubung dengan BangJoni\nSekarang share lokasimu dengan cara click tombol PIN dan tap Location", 0)
    return "Y" 


def uber_notified(event_id, event_time, event_type, meta_user_id, meta_resource_id, meta_resource_type, meta_status, resource_href):
    print "uber_notification>>>>XXXXX", event_id, event_time, event_type, meta_user_id, meta_resource_id, meta_resource_type, meta_status, resource_href
    stack.uber_send_notification(event_id, event_time, event_type, meta_user_id, meta_resource_id, meta_resource_type, meta_status, resource_href)

def push_billers_jatis(trxid, trxstatus, chart_table, payment_channel, trxtime):
    if trxstatus == "PENDING":
        status = trxstatus
    else:
        new_trxstatus = trxstatus.replace(". <br />","|")
        print new_trxstatus
        status = "SUCCESS"
        for item in new_trxstatus.split("|"):
            if "FAILED" in item:
                status = "FAILED"

    kode_bayar = ""    
    if "PENDING PAYMENT" in trxstatus and "KODE PEMBAYARAN" in trxstatus:
        status = "PENDING PAYMENT" 
        kode_bayar = trxstatus.split(":")[1]
				
    new_chart_table = chart_table
    if "\n" in new_chart_table:
        new_chart_table = chart_table.replace("\n",",")
    print new_chart_table
    msisdn_pln = ""
    token = ""	
    cat = ""
    jml_kwh = ""
    for item in new_chart_table.split(","):
        print item
        for x in ['TSEL','ISAT','XL/Axis','Three','Smartfren']:
            if x in item:
                msisdn_pln = item.split(":")[1].strip()
                #msisdn_pln = msisdn_pln.split(",")[0]			
                cat = "pulsa_hp"
        for x in ['PLN PREPAID','NO METER']:
            if x in item:				
                msisdn_pln = item.split(":")[1].strip()			
                #msisdn_pln = msisdn_pln.split(",")[0]			
                cat = "token"
        if 'STROOM/TOKEN' in item:
            token = item.split(":")[1].strip()	
        if 'JML KWH' in item:
            jml_kwh = item.split(":")[1].strip()			
				
        
    sql = "select * from jatis_billers where msisdn_pln = '%s' and (substr(dtm,1,10) = '%s' or status = '') limit 1" % (msisdn_pln, trxtime[:10])
    print sql
    sqlout = stack.request(sql)
    msisdn = ""
    for row in sqlout:
        msisdn = row[1]
		
    if msisdn != "" and (status == "SUCCESS" or status == "FAILED" or status == "PENDING PAYMENT"):
        if cat == "pulsa_hp": reply = "Sip, pembelian pulsa hp nomor %s sukses, cek di hpmu apakah pulsa sudah masuk" % (msisdn_pln)        	
        if cat == "token": reply = "Sip, pembelian token listrik nomor meter %s sukses, nomor tokenmu %s dengan jumlah KWH %s" % (msisdn_pln, token, jml_kwh)  		
        if status == "FAILED":
            reply = "Maaf nih, transaksi tidak dapat diproses, Bank akan segera refund 1x24jam jika saldomu kepotong"		
        if status == "PENDING PAYMENT":
            reply = "Segera lakukan pembayaran %s di %s dengan kode pembayaran %s agar transaksimu tidak dibatalkan" % (cat, payment_channel, kode_bayar)			
        stack.sendMessageT2(msisdn, reply, 0)
        sql = "update jatis_billers set trxid='%s', payment_channel='%s', status='%s' where lineid='%s' and msisdn_pln = '%s' and status = '' and substr(dtm,1,10) = '%s'" % (trxid, payment_channel, trxstatus, msisdn, msisdn_pln, trxtime[:10])
        print sql
        stack.insert(sql)  		
		
			
def handler(logDtm, msisdn, ask, first_name):
    if ask == "Delay":
        print "delay 10 second"
        time.sleep(10)
    #try:
    stack.onMessage(str(msisdn), ask, first_name)
    #except:
    #    print "There is an error"
    del incomingClient[msisdn]
    if msisdn == "139934550": print "thread deleted:", msisdn

def put_delay(n):
    time.sleep(n)
    print "Done"


if __name__==  "__main__":
    print "Telegram bang joni bot personal assistant is online"

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

	##############SETUP XSERVER & INIT GOPEGI CLASS 
    app_gui = init_qtgui()
    stack = TelegramGopegi()	
    
	###############GEVENT WSGI SERVER#################
    app = Flask(__name__)
    #app.debug = True

    @app.route('/hello')
    def home():
        return "Hello World!"
    
    @app.route('/loaderio-add028eafe5327db3904f06198dee0f7.txt')
    def verification():
        print "Verification"
        return "loaderio-add028eafe5327db3904f06198dee0f7"
    
    @app.route('/testload', methods=['POST'])
    def testload():
        content = request.get_json()
        print content
        return "OK"

    @app.route('/uber_token', methods=['GET'])
    def uber_token():
        state = request.args.get('state') 
        code = request.args.get('code') 
        print ""
        print "================================NEW UBER TOKEN REQUEST============================================="
        print state, code
        #g = gevent.spawn(uber_authorization, state, code)
        g = uber_authorization(state, code)		
        if g == "Y":
            return redirect('https://line.me/R/ch/1475301685', code=302)	
        else:
            return "OK"	

    @app.route('/uber_notified', methods=['POST'])
    def uber_notification():
        content = request.get_json()
        print ""
        print "================================NEW UBER NOTIF REQUEST============================================="
        print content
        event_id = ""
        event_time = ""
        event_type = ""
        meta_user_id = ""
        meta_resource_id = ""
        meta_resource_type = ""
        meta_status = ""
        resource_href = ""   
        if 'event_id' in content:
            event_id = str(content["event_id"])
        if 'event_time' in content:
            event_time = str(content["event_time"])
        if 'event_type' in content:
            event_type = str(content["event_type"])
        if 'user_id' in content["meta"]:
            meta_user_id = str(content["meta"]["user_id"])
        if 'resource_id' in content["meta"]:
            meta_resource_id = str(content["meta"]["resource_id"])
        if 'resource_type' in content["meta"]:
            meta_resource_type = str(content["meta"]["resource_type"])
        if 'status' in content["meta"]:
            meta_status = str(content["meta"]["status"])
        if 'resource_href' in content:
            resource_href = str(content["resource_href"])
        g = gevent.spawn(uber_notified, event_id, event_time, event_type, meta_user_id, meta_resource_id, meta_resource_type, meta_status, resource_href)
        print "reply OK"
        return "OK"

    @app.route('/uber_surge', methods=['GET'])
    def uber_surge():
        surge_confirmation_id = request.args.get('surge_confirmation_id') 
        print ""
        print "================================SURGE UBER NOTIF REQUEST============================================="
        print "surge_confirmation_id:", surge_confirmation_id
        g = gevent.spawn(stack.uber_request_ride_surge, surge_confirmation_id)
        return redirect(URL_TELEGRAM, code=302)

    @app.route('/callback_bangjoni', methods=['POST'])
    def jatis_callback():
        trxid = request.form.get('trxid')	
        merchant_name = request.form.get('merchant_name')	
        merchant_code = request.form.get('merchant_code')	
        payment_channel = request.form.get('payment_channel')	
        trxstatus = request.form.get('trxstatus')	
        chart_table = request.form.get('chart_table')	
        total_tagihan = request.form.get('total_tagihan')	
        total_pembayaran = request.form.get('total_pembayaran')	
        trxtime = request.form.get('trxtime')	
        content = request.form		
        print ""
        print "================================JATIS CALLBACK============================================="
        print "JATIS_CALLBACK:",trxid,merchant_name,merchant_code,payment_channel,trxstatus,chart_table,total_tagihan,total_pembayaran,trxtime
        print ">>>",content		
        g = gevent.spawn(push_billers_jatis, trxid, trxstatus, chart_table, payment_channel, trxtime)
        return "OK"		


		
    @app.route('/line1512', methods=['POST'])
    def bangjoni():
        content = request.get_json()
        print ""
        print "================================NEW LINE REQUEST============================================="
        print content
        msisdn = ""
        ask = ""
        longitude = ""
        latitude = ""
        username = ""
        first_name = ""
        last_name = ""
        phone_number = ""
        first_name_c = ""
        last_name_c = ""
        address = ""	
        sticker	= ""
        contentType = 0
		
        try:
            contentType = content["result"][0]["content"]["contentType"]
            msisdn = str(content["result"][0]["content"]["from"])	
            if contentType == 1:	
                ask = str(content["result"][0]["content"]["text"])
            if contentType == 7:
                longitude = content["result"][0]["content"]["location"]["longitude"]		
                latitude = content["result"][0]["content"]["location"]["latitude"]						
                address = content["result"][0]["content"]["location"]["address"]										
            if contentType == 8:
                sticker = content["result"][0]["content"]["contentMetadata"]["STKTXT"]					
            g = gevent.spawn(list_contents2, msisdn, ask, longitude, latitude, username, first_name, last_name, phone_number, first_name_c, last_name_c)				
            #linebot.send_images("uba6616c505479974378dadbd15aaeb77","http://128.199.88.72/line_images/139934550_cari.jpg","http://128.199.88.72/line_images/139934550_cari.jpg")
            #linebot.send_rich_message_payment_tiketdotcom("uba6616c505479974378dadbd15aaeb77","http://128.199.88.72/line_images/payment_tiketdotcom","Rich Message")						
            #linebot.send_rich_message_payment_tiketux("uba6616c505479974378dadbd15aaeb77","http://128.199.88.72/line_images/payment_tiketux","Rich Message")			
            #linebot.send_message("uba6616c505479974378dadbd15aaeb77","http://128.199.88.72")			
            #linebot.send_images_text("uba6616c505479974378dadbd15aaeb77","http://128.199.88.72/line_images/uba6616c505479974378dadbd15aaeb77_cari_20160915170335.jpg","http://128.199.88.72/line_images/uba6616c505479974378dadbd15aaeb77_cari_20160915170335.jpg", "Hello World")			
            #linebot.send_rich_message_payment_tiketdotcom_text("uba6616c505479974378dadbd15aaeb77","http://128.199.88.72/line_images/payment_tiketdotcom","Rich Message", "Hello World Again")			
            #linebot.send_link_message("uba6616c505479974378dadbd15aaeb77","berikut detail pesanannmu kjllkjsdlkfjsldjfsldkjfsldjfsldjfslkdjflsdkjflsdkjflksdjflsdkjflskdjflsdjflskdjflsdkjflkdsjflkdsjflkdsjfldsjflskdjfldskjfldskjflkdsj","www.bangjoni.com","Bayar Sekarang","http://128.199.88.72","http://128.199.88.72/line_images/logobangjoni2.jpg")			
            #stack.sendLinkMessageT2(msisdn, ' detailnya:\nKode Booking: %s\nKode Pembayaran: %s\nHarga: Rp. %s\nLakukan pembayaran sebelum %s.\nBang Joni kirim tiket jika pembayaran diterima.' % ('XX', 'YY', 'AA', 'BB'), 'www.bangjoni.com', 'Bayar Sekarang', 'http://128.199.88.72', 'http://128.199.88.72/line_images/logobangjoni2.jpg')			
        except:
            print "something error happen"	
            print content["result"]
            print "======"
            print content["result"][0]["content"]["contentType"]			
            print "======",msisdn,ask,longitude,latitude,sticker,address
            #linebot.send_message("uba6616c505479974378dadbd15aaeb77","Heloo world")
            #linebot.send_images("uba6616c505479974378dadbd15aaeb77","http://128.199.88.72/line_images/185808113_cari_line.jpg","http://128.199.88.72/line_images/xtrans_line.jpg")			
            #linebot.send_rich_message("uba6616c505479974378dadbd15aaeb77","http://128.199.88.72/line_images","Rich Message")			
        print "reply OK" 
        return "OK"

   
    print "starting gevent wsgi..."   
    #pywsgi.WSGIServer(('', 4000), app, keyfile=KEYFILE, certfile=CERTFILE).serve_forever()
    pywsgi.WSGIServer(('', 4000), app).serve_forever()


        

