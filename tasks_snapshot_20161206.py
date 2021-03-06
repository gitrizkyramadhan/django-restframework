# coding: utf-8
from celery import Celery

import time
import sys
from decimal import Decimal

from IMAPPush import Idler, idlerInit
from nlp_rivescript import Nlp
from html2png import Html2Png

from datetime import datetime, timedelta
import MySQLdb
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

import urllib
import requests
import httplib2

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

from bot import Bot

import random
import base64

import logging
import pickle

import hashlib
from operator import xor

# ---------- DWP MODULE START ----------
from ticket_dwp import DWP

# ---------- ECOMM MODULE START ----------
from merchant_commerce import MerchantCommerce

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


linebot = Bot()
lineNlp = Nlp()
app_gui = init_qtgui()
lineHtml2Png = Html2Png()
dwp = DWP()
mcomm = MerchantCommerce()

app = Celery('tasks', backend = 'amqp', broker = 'amqp://')

F_SRVC = None
F_BOOK = None
F_PAID = None
F_NOREPLY = None
F_ADDFRIENDS = None


def setup_logger(loggername, logfile):
        l = logging.getLogger(loggername)
        fileHandler = logging.FileHandler(logfile, mode='a')
        streamHandler = logging.StreamHandler()
        l.setLevel(level=logging.INFO)
        l.addHandler(fileHandler)
        l.addHandler(streamHandler)

def save_last10chat(dtm, msisdn, mesg, actor):
    chat = str(dtm) + "|" + str(msisdn) + "|" + str(mesg) + "|" + str(actor)
    id = "savedchat/" + msisdn
    chat_len = len(lineNlp.redisconn.lrange(id,0,-1))
    if chat_len > 10:
        lineNlp.redisconn.lpop(id)
    lineNlp.redisconn.rpush(id, chat)	
		
def request(sql):
        try:
            db_connect = MySQLdb.connect(host = MYSQL_HOST, port = 3306, user = MYSQL_USER, passwd = MYSQL_PWD, db = MYSQL_DB)
            # Create cursor
            cursor = db_connect.cursor()
            cursor.execute(sql)
            sqlout = cursor.fetchall()
            return sqlout
        except MySQLdb.Error, e:
            logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
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
            logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
            print e.args
            print "ERROR: %d: %s" % (e.args[0], e.args[1])
            
def fetchJSON(url):
        (resp_headers, content) = connAPI.request(url, "GET")    

        try:
           decoded = json.loads(content)
           #print json.dumps(decoded, sort_keys=True, indent=4)
           return decoded
        except (ValueError, KeyError, TypeError):
           print "JSON format error"

#def fetchHTML(url):
#        try:
#           r = requests.get(url)
#           print "resp html: ", r.content
#           return r.content
#        except Exception as e:
#           print ">>Error is:",e

def fetchHTML(url):
    connAPI = httplib2.Http()
    try:
       (resp_headers, content) = connAPI.request(url, "GET")    
       #print ">>resp_header", resp_headers
       return content
    except Exception as e:
       print ">>Error is:",e		   


def sendMessageTX(msisdn, message, keyboard):
        linebot.send_message(msisdn, message.strip())
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')		
        save_last10chat(logDtm, msisdn, message.strip(), 'BJ')		

def sendPhotoTX(msisdn, file_path, caption, keyboard):
        print "---------->", file_path.split('/')[6]
        linebot.send_images(msisdn,"http://128.199.88.72/line_images/%s" % (file_path.split('/')[6]), "http://128.199.88.72/line_images/%s" % (file_path.split('/')[6]))			
	
def sendMessageT2(msisdn, message, keyboard = 0):
        sendMessageTX(msisdn, message, keyboard)

def sendPhotoT2(msisdn, file_path, caption = "", keyboard = 0):
        sendPhotoTX(msisdn, file_path, caption, keyboard) 
		
def sendPhotoCaptionT2(msisdn, link_url, previewImageUrl, message):
        linebot.send_images_text(msisdn, link_url, previewImageUrl, message.strip())
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')		
        save_last10chat(logDtm, msisdn, message.strip(), 'BJ')				

def sendRichCaptionT2(msisdn, link_url, message, keyboard):
        if keyboard == "tiketux":        
            linebot.send_rich_message_payment_tiketux_text(msisdn, link_url,"Rich Message", message.strip())
        if keyboard == "tiketdotcom":        
            linebot.send_rich_message_payment_tiketdotcom_text(msisdn, link_url,"Rich Message", message.strip())
        if keyboard == "tokenpln":        
            linebot.send_rich_message_token_pln_text(msisdn, link_url,"Rich Message", message.strip())	
        if keyboard == "pulsahp":        
            linebot.send_rich_message_pulsa_hp_text(msisdn, link_url,"Rich Message", message.strip())				
        if keyboard == "jatis":        
            linebot.send_rich_message_payment_jatis_text(msisdn, link_url,"Rich Message", message.strip())
        if keyboard == "bjpayregister":        
            linebot.send_rich_message_bjpay_register_text(msisdn, link_url,"Rich Message", message.strip())			
        if keyboard == "bjpaydeposit":        
            linebot.send_rich_message_bjpay_deposit_text(msisdn, link_url,"Rich Message", message.strip())				
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')		
        save_last10chat(logDtm, msisdn, message.strip(), 'BJ')				
			
def sendLinkMessageT2(msisdn, message1, message2, message3, link_url, previewImageUrl):
        # print "-x-x-x-x-x-x-", message1, message2, message3, link_url
        linebot.send_link_message(msisdn, message1.strip(), message2, message3, link_url, previewImageUrl)
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')		
        save_last10chat(logDtm, msisdn, message1.strip(), 'BJ')			
		
def log_service(logDtm, msisdn, first_name, service, desc = 'None'):      
        #sql = "insert into request_service values('" + logDtm + "','" + msisdn + "','" + first_name + "','" + service + "')"
        sql = logDtm + "," + msisdn + "," + first_name + "," + service + "," + desc
        F_SRVC.info(sql)

def log_book(logDtm, msisdn, first_name, service, desc = 'None'):      
        sql = logDtm + "," + msisdn + "," + first_name + "," + service + "," + desc
        F_BOOK.info(sql)		

def log_paid(logDtm, msisdn, first_name, service, desc = 'None'):      
        sql = logDtm + "," + msisdn + "," + first_name + "," + service + "," + desc
        F_PAID.info(sql)		

def log_addfriends(logDtm, msisdn, first_name, service, desc = 'None'):      
        sql = logDtm + "," + msisdn + "," + first_name + "," + service + "," + desc
        F_ADDFRIENDS.info(sql)				

def get_line_username(msisdn):
        sql = "select * from line_users where user_id = '%s'" % (msisdn)
        sqlout = request(sql)
        first_name = "";
        for row in sqlout:
            first_name = row[1]   
        print sql, first_name
        if first_name != "":
            return first_name
        else:
            r = requests.get("https://api.line.me/v1/profiles?mids=%s" % (msisdn), headers={'Content-Type': 'application/json', 'X-LINE-ChannelToken': 'NXLU6oHQJxMzsUwJLUiWgSGKOG6J+l9/gUx+p0qtI5wdfx063TL55RQ1QzocuBIETSwUY98USKR+MhG5Ndq1dBFYmzjXa3UfUn8iCD7ShHVtZZ4eLTZe0xVuMBd9pyDUtfGctFIIjC3W+kRVkxGUka18BSl7lGXPAT9HRw/DX2c='})
            rjson = json.loads(r.content)
            try:			
                sql = "insert into line_users values('" + msisdn + "','" + rjson["contacts"][0]["displayName"] + "')"
                print sql
                insert(sql)  			
                return rjson["contacts"][0]["displayName"]        
            except:
                return "bro/sis"

def onEmailReceived(filename, filetype):
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')				
        print("%s email received %s" % (logDtm, filename))  
        state = 0
        
        if filetype == "pdf":   
            sql = "select * from booking_tickets where order_id = '%s'" % (filename.split(':')[0])
            print sql
            sqlout = request(sql)
            msisdn = "";
            for row in sqlout:
                msisdn = row[1]

            if msisdn == "":
                sql = "select * from booking_xtrans where kodebooking = '%s'" % (filename.split(':')[1].split('.')[0])
                print sql
                sqlout = request(sql)
                msisdn = "";
                for row in sqlout:
                    msisdn = row[0]
                if msisdn != "": 
                    displayname = get_line_username(msisdn)				
                    log_paid(logDtm, msisdn, displayname, "XTRANS")
            else:
                displayname = get_line_username(msisdn)			
                log_paid(logDtm, msisdn, displayname, "FLIGHT")
					
            if msisdn != "":
                pdffilename = str(filename.split(':')[1])
                pdf_im = PyPDF2.PdfFileReader(file("/tmp/%s" % (pdffilename), "rb"))
                npage = pdf_im.getNumPages()
                print("Converting %d pages" % npage)
                for p in range(npage):
                    pdf2jpg = PythonMagick.Image()
                    pdf2jpg.density("200")
                    pdf2jpg.read("/tmp/%s[%d]" % (pdffilename, p))
                    pdffilename1 = pdffilename.replace("#","")
                    pdf2jpg.write("/usr/share/nginx/html/line_images/%sP%d.jpg" % (pdffilename1.split('.')[0], p))
                    print("%s send attachment %s page %d to %s" % (logDtm, filename, p, msisdn))
                    sendPhotoT2(msisdn, '/usr/share/nginx/html/line_images/%sP%d.jpg' % (pdffilename1.split('.')[0], p))
        
        elif filetype == "html":
            sql = "select * from booking_tickets where order_id = '%s'" % (filename.split('.')[0])
            print sql
            sqlout = request(sql)
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
                   sendMessageT2(msisdn, "Tiket pesawat kamu sudah Bang Joni booking.\nSilakan lakukan transaksi pembayaran tiket pesawat kamu via ATM. \nTiket otomatis dikirim jika pembayaran telah diterima, maks 60 menit.", 0)  
        
        else:
            sql = "select * from booking_tickets where order_id = '%s'" % (filename.split('.')[0])
            print sql
            sqlout = request(sql)
            msisdn = "";
            for row in sqlout:
                msisdn = row[1]

            if msisdn == "":    
                state = 1
                sql = "select * from booking_train where order_id = '%s'" % (filename.split('.')[0])
                print sql
                sqlout = request(sql)
                msisdn = "";
                for row in sqlout:
                    msisdn = row[1]

            if msisdn == "":
                state = 2
                sql = "select * from booking_xtrans where kodebooking = '%s'" % (filename.split('.')[1])
                print sql
                sqlout = request(sql)
                msisdn = "";
                for row in sqlout:
                    msisdn = row[0]

            if msisdn != "":                       
                sendMessageT2(msisdn, filetype)
                
                #Artajasa payment info for tiket.com
                if filetype.find("Artajasa") >= 0:  
                    sendPhotoT2(msisdn, 'images/artajasa_payment.png')
        return 1			
			

def submit_unknown_agent(msisdn, ask, first_name):
    url = "http://localhost:3000/bangjoni2/{\"user\":\"%s\",\"msg\":\"%s\",\"msisdn\":\"%s\"}" % (first_name, ask, msisdn)	
    try:
        print url
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print ">>Error HTTP to facebook chat server:",e

# ---------- DWP MODULE START ----------
def do_dwp_event(msisdn, ask, first_name, answer, incomingMsisdn):
    logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
    log_service(logDtm, msisdn, first_name, "DWP")
    if answer[:5] == "dwp00":
        sendMessageT2(msisdn, answer[5:], 0)
        linebot.send_rich_message_dwp_discount(msisdn, '','')
    elif answer[:5] == "dwp01":
        sendMessageT2(msisdn, answer[5:], 0)
        linebot.send_rich_message_dwp_tickets(msisdn, "http://bangjoni.com/dwp_images/dwp_ticket_free_1","Ticket DWP beli 5 gratis 1")
    elif answer[:5] == "dwp06":
        sendMessageT2(msisdn, answer[5:], 0)
        linebot.send_rich_message_dwp_tickets(msisdn, "http://bangjoni.com/dwp_images/dwp_ticket_disc_15","Ticket DWP dis")
        # TODO kirim gambar pilihan jenis tiket
    elif answer[:5] == "dwp04":
        quantity = int(incomingMsisdn[14])
        discType = int(incomingMsisdn[15])
        if quantity > 4 and discType == 1:
            answer = dwp_error_msg(1005,msisdn,first_name)
            sendMessageT2(msisdn, answer, 0)
        else:
            answer = answer.replace("dwp04","")
            sendMessageT2(msisdn, answer, 0)
    elif answer[:5] == "dwp05":
        quantity = incomingMsisdn[14]
        discType = incomingMsisdn[15]
        ticketCategory = incomingMsisdn[16]
        # ticketCategory = "Regular Single" #TODO hilangin kategori tiket buat production
        identity = [s.strip() for s in ask.splitlines()]
        if len(identity) != 6:
            dwp_input_invalid(msisdn, first_name)
        else:
            firstName = identity[0]
            idNumber = identity[1]
            dob = identity[2].replace(" ","-")
            gender = identity[3]
            email = identity[4]
            phone = identity[5]
            uid = msisdn
            result = dwp.bookTickets(ticketCategory, quantity, firstName, '', idNumber, dob, gender, email, phone, uid, discType)
            answer = answer[5:]
            if result.get('error_code') :
                answer = dwp_error_msg(result['error_code'], msisdn, first_name)
            else:
                answer = answer.replace("<dwp_book_code>",result['data']['invoice_code'])
                answer = answer.replace("<dwp_amount_to_pay>", '{0:,}'.format(Decimal(result['data']['amountpay'])))
                answer = answer.replace("<dwp_max_book_time>", result['data']['max_book_time'])
            sendMessageT2(msisdn, answer, 0)
            #todoreminder
    else:
        sendMessageT2(msisdn, answer[5:], 0)

def dwp_input_invalid(msisdn, first_name):
    # rejectAnswer = lineNlp.doNlp("inputinvalid", msisdn, first_name)
    # rejectAnswer = "Format yang kamu isikan salah. Cek format isiannya ya,\n\nNama\nNo. Identitas\nTanggal Lahir (DD-MM-YYYY)\nJenis Kelamin (L/P)\nEmail\nNo. HP"
    rejectAnswer = lineNlp.doNlp("inputinvalid", msisdn, first_name)
    sendMessageT2(msisdn, rejectAnswer, 0)

def dwp_error_msg(errorCode, msisdn, first_name):
    # print "Error code DWP :: "+errorCode
    if errorCode == 1001 or errorCode == 1002 or errorCode == 1003 : errKeyword = "dwpticketnotavailable"
    elif errorCode == 1004: errKeyword =  "dwpticketregistereduser"
    elif errorCode == 1005: errKeyword =  "dwpticketqtyviolation"
    elif errorCode == 1006 or errorCode == 1007: errKeyword =  "dwpticketbookingamtviolation"
    elif errorCode == 1008: errKeyword =  "dwpticketdateinvalidformat"
    elif errorCode == 1011: errKeyword =  "dwpticketpendingbook"
    elif errorCode == 1012: errKeyword =  "dwpticketinvalidemail"
    rejectAnswer = lineNlp.doNlp(errKeyword, msisdn, first_name)
    return rejectAnswer

    # if errorCode == 1001 or errorCode == 1002 or errorCode == 1003 : return "Tiket tidak tersedia"
    # elif errorCode == 1004: return  "Kamu sudah pernah pesan tiket DWP, tunggu tahun depan buat pesen lagi"
    # elif errorCode == 1005: return  "Bang Joni batesin dulu per orang 4 tiket ya, jangan banyak2 :P"
    # elif errorCode == 1006 or errorCode == 1007: return  "Pembayaran kamu udah Bang Joni terima, tapi masih jumlahnya ga sesuai nih, segera kontak call center Bang Joni ya"
    # elif errorCode == 1008: return  "dwp_ticket_date_invalid_format"
    # elif errorCode == 1011: return  "dwp_ticket_pending_book"

# ---------- DWP MODULE END ----------

# ---------- LOVIDOVI MODULE START ----------
def do_lovidovi_event(msisdn, ask, first_name, answer, incomingMsisdn):
    logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
    # log_service(logDtm, msisdn, first_name, "LOVIDOVI")
    if answer[:5] == "lov01":
        sendMessageT2(msisdn, answer[5:], 0)
        sendLinkMessageT2(msisdn, "Lovidovi", "Tap untuk lihat kateori bunga", "Lihat kategori", "http://139.59.244.156/lovidovi/products.php?userid="+msisdn, "https://pbs.twimg.com/profile_images/761463627819790336/rrxISonW.jpg")
    else :
        sendMessageT2(msisdn, answer[5:], 0)
    print "oit"
# ---------- LOVIDOVI MODULE END ----------

# ---------- ECOMMERCE MODULE START ----------
def do_ecommerce_event(msisdn, ask, first_name, answer, incomingMsisdn):
    incomingMsisdn[11] = "eco00"
    if answer[:5] == "eco04":
        custName = incomingMsisdn[14].split("/")[0]
        custAddress = incomingMsisdn[14].split("/")[1]
        custContact = incomingMsisdn[14].split("/")[2]
        orderDetail = "Kamu mendapat order :: "+incomingMsisdn[15].split("/")[0]+" sejumlah :: "+incomingMsisdn[15].split("/")[1]
        respJson = mcomm.createOrder(msisdn, msisdn, custName, custAddress, custContact, incomingMsisdn[2], incomingMsisdn[3], notes = '', detail = orderDetail)
        if respJson['status'] != '200':
            if respJson['status'] == '500':
                print respJson['status']
                answer = lineNlp.doNlp("systemfailure", msisdn, first_name)
                sendMessageT2(msisdn, answer, 0)
            elif respJson['status'] == '1001':
                answer = lineNlp.doNlp("merchantnotfound", msisdn, first_name)
                sendMessageT2(msisdn, answer, 0)
        else:
            answer = lineNlp.doNlp("merchantready", msisdn, first_name)
            answer = answer.replace("<merchant_count>", respJson['merchantFound'])
            sendMessageT2(msisdn, answer[5:], 0)
    else :
        sendMessageT2(msisdn, answer[5:], 0)
    print "handle ecommerce"
# ---------- ECOMMERCE MODULE END ----------

def onMessage(msisdn, ask, first_name):                                     
        if ask[:5] != "[LOC]":
            #ask = ask.translate(None, ",!.?$%").lower()
            #ask = ask.translate(None, "!?$%").lower()
            ask = ask.replace("-"," ")
            ask = ask.replace("!","")
            ask = ask.replace("?","")
            ask = ask.replace("$","")
            ask = ask.replace("\\","")
            ask = ask.replace("%","").lower()
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')    
        answer = ""                
        print "--------------------------------------------------->",logDtm, msisdn, ask

        if lineNlp.redisconn.exists("inc/%s" % (msisdn)):	
            incomingMsisdn = json.loads(lineNlp.redisconn.get("inc/%s" % (msisdn)))		
            last_request = datetime.strptime(incomingMsisdn[12],'%Y-%m-%d %H:%M:%S')
            new_request = datetime.strptime(logDtm,'%Y-%m-%d %H:%M:%S')
            if (new_request - last_request).total_seconds() > 1800: #reset request after half an hour
                incomingMsisdn = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""]
                answer = lineNlp.doNlp("ga jadi", msisdn, first_name)
        else:
            incomingMsisdn = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""] 
        lineNlp.redisconn.set("inc/%s" % (msisdn), json.dumps(incomingMsisdn))			
            
        ask_temp = ask
        save_last10chat(logDtm, msisdn, ask, first_name)		
        if ask[:5] != "[LOC]":
            
            answer = lineNlp.doNlp(ask, msisdn, first_name)	
            incomingMsisdn = json.loads(lineNlp.redisconn.get("inc/%s" % (msisdn)))
            print "_____________________>", answer, incomingMsisdn			
            if (answer[:2] == "ee" and (incomingMsisdn[11] == "xt01" or incomingMsisdn[11] == "xt02")):
                ask = lineNlp.spell_correctness3(ask)
                print "correctness to: ", ask
                answer = lineNlp.doNlp(ask, msisdn, first_name)
                incomingMsisdn = json.loads(lineNlp.redisconn.get("inc/%s" % (msisdn)))				
                incomingMsisdn[11] == ""
                print "-->", answer

            if answer[:2] == "ee" and incomingMsisdn[11] == "ke00":
                ask = lineNlp.spell_correctness2(ask, city_train)
                print "correctness to: ", ask
                answer = lineNlp.doNlp(ask, msisdn, first_name)
                incomingMsisdn = json.loads(lineNlp.redisconn.get("inc/%s" % (msisdn)))				
                if answer[:2] == "ee": 
                    incomingMsisdn[11] == "ke00"
                else:
                    incomingMsisdn[11] == ""
                print "-->", answer

            if (answer[:2] == "fl" or answer[:2] == "xt" or answer[:2] == "ke" or answer[:2] == "ub" or answer[:2] == "ca" or answer[:2] == "zo" or answer[:2] == "ch" or answer[:2] == "ee" or answer[:2] == "gr" or answer[:2] == "we" or answer[:2] == "to" or answer[:2] == "ka" or answer[:2] == "sh" or answer[:2] == "eu" or answer[:2] == "re" or answer[:2] == "sh" or answer[:2] == "rs" or answer[:2] == "sc" or answer[:2] == "tr" or answer[:2] == "pl" or answer[:2] == "pu" or answer[:3] == "dwp" or answer[:3] == "lov" or answer[:3] == "eco" or answer[:2] == "bj") and incomingMsisdn[1] != "TRANSLATOR_MODE":
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
                    # ---------- DWP MODULE ADD EXCLUSION ----------
                    if answer[:4] != "gr01" and answer[:4] != "ub01" and answer[:4] != "xt08" and answer[:4] != "fl05" and answer[:4] != "ka01" and answer[:4] != "xt01" and answer[:4] != "xt06" and answer[:4] != "xt04" and answer[:4] != "pu01" and answer[:4] != "pl02" and answer[:4] != "pu02" and answer[:3] != "dwp" and answer[:3] != "lov" and answer[:3] != "eco":
                        sendMessageT2(msisdn, temp_answer, 0)
                    if answer[:4] == "xt08":
                        sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/payment_tiketux1', answer.replace('xt08 ',''), 'tiketux')					
                    if answer[:4] == "fl05":
                        sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/payment_tiketdotcom1', answer.replace('fl05 ',''), 'tiketdotcom')
                # ---------- DWP MODULE START ----------
                if answer[:3] == "dwp":
                    do_dwp_event(msisdn, ask, first_name, answer, incomingMsisdn)
                # ---------- DWP MODULE END ----------
                # ---------- LOVIDOVI MODULE START ----------
                if answer[:3] == "lov":
                    do_lovidovi_event(msisdn, ask, first_name, answer, incomingMsisdn)
                # ---------- LOVIDOVI MODULE END ----------
                # ---------- ECOMMERCE MODULE START ----------
                if answer[:3] == "eco":
                    do_ecommerce_event(msisdn, ask, first_name, answer, incomingMsisdn)
                # ---------- ECOMMERCE MODULE END ----------

            else: 
                if incomingMsisdn[1] != "TRANSLATOR_MODE":
                    sendMessageT2(msisdn, answer, 0)



####################GREETINGS####################
        if answer[:4] == "gr01":
            linebot.send_rich_message_greeting_text(msisdn, 'https://www.bangjoni.com/line_images/halo1','RICH MESG',temp_answer.strip())
#################################################

####################PULSA START####################
        if answer[:4] == "pu01":
            log_service(logDtm, msisdn, first_name, "PULSA")		
            print incomingMsisdn[2]
            reply = "Berikut harga pulsa %s :\n" % (incomingMsisdn[2])
            x = ['5K','10K','20K','25K','50K','100K']
            y = [5000,10000,20000,25000,50000,100000]			
            i = 0
            for item in incomingMsisdn[3].split('|'):
                z = y[i] + int(item)
                if item != "99":
                    reply = reply + x[i] + " Rp. %d" % (z) + "\n"
                i = i + 1
            reply = reply + "Untuk memilih nominal pulsa, tap menu dibawah."
            #print reply
            sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/pulsa_hp1', reply, 'pulsahp')	
			
        if answer[:4] == "pu02":
            #sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/payment_jatis1', answer[4:], 'jatis')			
            #print incomingMsisdn[1],incomingMsisdn[5]		
            if lineNlp.redisconn.exists("bjpay/%s" % (msisdn)):		
                print "USER HAS BJPAY"				
                #Check BJPAY Balance
                payload = lineNlp.redisconn.get("bjpay/%s" % (msisdn))
                balance = int(payload.split('|')[0])
                va_no = payload.split('|')[1]
                deposit_hp = payload.split('|')[2] 							
                if balance >= (incomingMsisdn[5] + 1000):	
                    print balance, incomingMsisdn[5] + 1000				
                    r = (datetime.now() + timedelta(hours=0)).strftime('%H%M%S')
                    partner_trxid = r + incomingMsisdn[1][-4:] 					
                    s = r + incomingMsisdn[1][-4:]
                    m = incomingMsisdn[1][-4:][::-1] + 'kingsm'
                    s=''.join(chr(ord(a)^ord(b)) for a,b in zip(s,m))
                    sign = s.encode('base64').strip()
                    print sign.strip()

                    xml = '<?xml version="1.0" ?> <evoucher>'
                    xml = xml + '<command>TOPUP</command>'
                    xml = xml + '<product>' + incomingMsisdn[4] + '</product>'
                    xml = xml + '<userid>bangjoni</userid>'
                    xml = xml + '<time>' + r + '</time>'
                    xml = xml + '<msisdn>' + incomingMsisdn[1] + '</msisdn>'
                    xml = xml + '<partner_trxid>' + partner_trxid + '</partner_trxid>'
                    xml = xml + '<signature>' + sign + '</signature>'
                    xml = xml + '</evoucher>'

                    print xml

                    headers = {'Content-Type': 'text/xml'}
                    resp = requests.post('https://cyrusku.cyruspad.com/interkoneksi/interkoneksicyrusku.asp', data=xml, headers=headers)
                    print resp.text
                    parsed_xml = BeautifulSoup(resp.text)
                    response = parsed_xml.evoucher.result.string
                    msg = parsed_xml.evoucher.msg.string			
                    print response, msg					
                    if response == "0":
                        answer = "Bang Joni berhasil isiin pulsamu, berikut informasi serial number-nya:\n%s" % (msg.split('S/N ')[1])					
                        # decrement saldo
                        debit = int(msg.split('(Rp ')[1].split(')')[0])
                        balance = balance - debit - 200		
                        payload = balance + "|" + va_no + "|" + deposit_hp						
                        lineNlp.redisconn.set("bjpay/%s" % (msisdn), payload)						
                    else:
                        answer = "Sorry nih, Bang Joni gak bisa isiin pulsanya, %s, coba lagi ya..." % (msg.split('.')[0])										
                    sendMessageT2(msisdn, answer, 0)						
                else:					
                    sendMessageT2(msisdn, "Balance BJPAY-mu tidak cukup, untuk Top up ketik aja topup bjpay", 0)									

            else:
                sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/bjpay_register', answer[4:], 'bjpayregister')
				
			
        if answer[:4] == "bj02":				
            r = (datetime.now() + timedelta(hours=0)).strftime('%Y%m%d%H%M%S')
            signature = hashlib.md5('bangjoni' + r + 'bang567jon1').hexdigest()
            merchant_trx_id = r + incomingMsisdn[6][-4:].zfill(4)
            va_no = "865010" + incomingMsisdn[6][-10:].zfill(10)

            #Register VA
            payload = { 'command': 'registerva', 'username': 'bangjoni', 'time': r, 'va_no': va_no, 'bank': 'Permata', 'cust_id': incomingMsisdn[6], 'cust_name': first_name, 'pay_type': 'Partial', 'amount': '10000', 'signature': signature }			
            print payload			
            headers = {'content-type': 'application/json'}
            resp = requests.post('https://cyrusku.cyruspad.com/pgw/pgwapi.asp', data=json.dumps(payload), headers=headers)
            content = resp.text    
            print content			
            content = json.loads(content)			
            response = content['Response']
            message = content['Message']
            if response == "0":
                payload = "0|" + va_no + "|" + incomingMsisdn[6]			
                lineNlp.redisconn.set("bjpay/%s" % (msisdn), payload)				
                answer = "Pendaftaran BJPAY berhasil, selanjutnya pilih bank berikut dengan tap logo bank untuk deposit"
            elif response == "107":				
                answer = "Pendaftaran BJPAY sudah pernah sebelumnya"				
            else:
                answer = "Bang Joni gak register BJPAY, coba lagi ya..."
            sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/bjpay_deposit', answer, 'bjpaydeposit')					

        if answer[:4] == "bj04":					
            if incomingMsisdn[7] != "va permata":
                r = (datetime.now() + timedelta(hours=0)).strftime('%Y%m%d%H%M%S')
                signature = hashlib.md5('bangjoni' + r + 'bang567jon1').hexdigest()
                merchant_trx_id = r + incomingMsisdn[6][-4:].zfill(4)			
                payload = { 'command': 'banktransfer', 'username': 'bangjoni', 'time': r, 'amount': incomingMsisdn[8], 'description': 'Beli Saldo MStar', 'merchant_trx_id': merchant_trx_id, 'signature': signature }
                print payload			
                headers = {'content-type': 'application/json'}
                resp = requests.post('https://cyrusku.cyruspad.com/pgw/pgwapi.asp', data=json.dumps(payload), headers=headers)
                content = resp.text
                print content
                content = json.loads(content)
                response = content['Response']
                if response == "0":				
                    trx_id = content['trx_id']			
                    transfer_amount = content['transfer_amount']
                    sql = "insert into bjpay values('%s','%s','',%s,'')" % (msisdn, r, transfer_amount)
                    print sql
                    insert(sql)  										
                    answer = "Lakukan transfer Rp %s (harus sesuai) max 3 jam dari sekarang ke bank berikut:" % (transfer_amount)					 
                    for bank in content['bank_info']:
                        answer = answer + "\n\nBank: " + bank['bank'] + "\nNo Rekening: " + bank['account_no'] + "\nAn: " + bank['account_name']					
            else:						
                payload = lineNlp.redisconn.get("bjpay/%s" % (msisdn))
                va_no = payload.split('|')[1]
                deposit_hp = payload.split('|')[2] 				
                sql = "insert into bjpay values('%s','%s','%s',%s,'%s')" % (msisdn, r, va_no, incomingMsisdn[8], deposit_hp)
                print sql
                insert(sql)  					
                answer = "Lakukan transfer Rp %s ke Bank Permata no rekening an %s dan HP %s:" % (incomingMsisdn[8], va_no, deposit_hp)  
						
            sendMessageT2(msisdn, answer, 0)					
					
	
			
        if answer[:4] == "pu03":		
            print incomingMsisdn[3]		
            params = {'itemtype': incomingMsisdn[5], 'accountnumber': incomingMsisdn[1], 'merchantid': 'bangjoni', 'btnsubmit':'Beli'}
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
                incomingMsisdn[6] = soup.find('input', {'id': 'client_ip'}).get('value')	
                incomingMsisdn[7] = soup.find('input', {'id': 'id_biller'}).get('value')
                incomingMsisdn[8] = soup.find('input', {'id': 'merchant_id'}).get('value')	
                incomingMsisdn[9] = soup.find('input', {'id': 'merchant_code'}).get('value')
                incomingMsisdn[10] = soup.find('input', {'id': 'basket'}).get('value')		
                incomingMsisdn[11] = soup.find('input', {'id': 'nominal'}).get('value')	
                incomingMsisdn[13] = soup.find('input', {'id': 'account_number'}).get('value')	
                incomingMsisdn[14] = soup.find('input', {'id': 'item_type'}).get('value')	
                incomingMsisdn[15] = soup.find('input', {'id': 'production'}).get('value')							
            except:
                print "Error bs4"
			
            sqlstart = content.find("Total Price")
            if sqlstart > -1:
                log_book(logDtm, msisdn, first_name, "PULSA", incomingMsisdn[1] + "-" + incomingMsisdn[11])	
                content = content[sqlstart:]     
                content = content[:content.find("</table>")]		
                total_price = int(re.findall(r'\d+',content)[-1])
                merchantamount = total_price
                print ">>",content, total_price	   
                print incomingMsisdn				
			
                params = {'id_biller': incomingMsisdn[7], 'payment_channel': incomingMsisdn[3], 'totalamount': total_price}
                print ">>>>>>",params
                resp = requests.post('http://corepay.mobeli.co.id/jswitch/get_pg_amount2', data=params)	
                content = json.loads(resp.text)	
                pgamount = content['pgamount']
                print incomingMsisdn, total_price, pgamount

                if incomingMsisdn[3] != "2": #NON ECASH PAYMENT
                    #url_pay = 'http://128.199.88.72/pulsa/go_pulsa1.php?payment_channel=%s&client_ip=%s&id_biller=%s&merchant_id=%s&merchant_code=%s&basket=%s&total_price=%s&merchantamount=%s&pgamount=%s&nominal=%s&account_number=%s&item_type=%s&production=%s' % (incomingMsisdn[3],incomingMsisdn[6],incomingMsisdn[7],incomingMsisdn[8],incomingMsisdn[9],incomingMsisdn[10],total_price,merchantamount,pgamount,incomingMsisdn[11],incomingMsisdn[13],incomingMsisdn[14],incomingMsisdn[15])
                    url_pay = 'http://128.199.139.105/pulsa/go_pulsa2.php?msisdn=%s&p=pulsa' % (msisdn)					
                    url_post = 'payment_channel=%s&client_ip=%s&id_biller=%s&merchant_id=%s&merchant_code=%s&basket=%s&total_price=%s&merchantamount=%s&pgamount=%s&nominal=%s&account_number=%s&item_type=%s&production=%s' % (incomingMsisdn[3],incomingMsisdn[6],incomingMsisdn[7],incomingMsisdn[8],incomingMsisdn[9],incomingMsisdn[10],total_price,merchantamount,pgamount,incomingMsisdn[11],incomingMsisdn[13],incomingMsisdn[14],incomingMsisdn[15])					
                    lineNlp.redisconn.set(msisdn + "/pulsa", url_post)										
                    print url_pay
                    sendLinkMessageT2(msisdn, 'berhasil pesen pulsa handphone %s dengan harga %s (include biaya administrasi)' % (incomingMsisdn[11], pgamount), 'DOKU Payment', 'Bayar Sekarang', url_pay, 'http://128.199.88.72/line_images/logobangjoni2.jpg')				
                else:					
                    params = {'payment_channel': incomingMsisdn[3], 'client_ip': incomingMsisdn[6], 'id_biller': incomingMsisdn[7], 'merchant_id': incomingMsisdn[8], 'merchant_code': incomingMsisdn[9], 'basket': incomingMsisdn[10], 'total_price': total_price, 'merchantamount': merchantamount, 'pgamount': pgamount, 'nominal': incomingMsisdn[11], 'account_number': incomingMsisdn[13], 'item_type': incomingMsisdn[14], 'production': incomingMsisdn[15]}
                    resp = requests.post('http://128.199.88.72/pulsa/go_pulsa.php', data=params)	
                    content = resp.text
                    #print content

                    sqlstart = content.find("<REDIRECT>https://mandiriecash.com/ecommgateway")
                    if sqlstart > -1:
                        print "eCash PAY"				
                        url_pay = content[sqlstart+10:content.find("</REDIRECT>")]
                        sendLinkMessageT2(msisdn, 'berhasil pesen pulsa handphone %s dengan harga %s (include biaya administrasi)' % (incomingMsisdn[11], pgamount), 'Mandiri eCash', 'Bayar Sekarang', url_pay, 'http://128.199.88.72/line_images/logobangjoni2.jpg')							
						
                sql = "insert into jatis_billers values('" + incomingMsisdn[1] + "','" + msisdn + "','none','" + logDtm + "','" + incomingMsisdn[3] + "','')"
                print sql
                insert(sql)													
						
            answer = lineNlp.doNlp("ga jadi", msisdn, first_name)						
	
				
			
####################TOKEN START####################
        if answer[:4] == "pl01":
            log_service(logDtm, msisdn, first_name, "PLN")
            params = {'itemtype': '3|9950102', 'accountnumber': incomingMsisdn[1], 'merchantid': 'bangjoni', 'btnsubmit':'Beli'}
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
                sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/token_pln1', reply, 'tokenpln')	
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
                    incomingMsisdn[4] = soup.find('input', {'id': 'client_ip'}).get('value')	
                    incomingMsisdn[5] = soup.find('input', {'id': 'id_biller'}).get('value')
                    incomingMsisdn[6] = soup.find('input', {'id': 'systrace'}).get('value')	
                    incomingMsisdn[7] = soup.find('input', {'id': 'inquiryid'}).get('value')	
                    incomingMsisdn[8] = soup.find('input', {'id': 'billerid'}).get('value')	
                    incomingMsisdn[9] = soup.find('input', {'id': 'biller_name'}).get('value')	
                    incomingMsisdn[10] = soup.find('input', {'id': 'merchant_id'}).get('value')	
                    incomingMsisdn[11] = soup.find('input', {'id': 'merchant_code'}).get('value')	
                    incomingMsisdn[13] = soup.find('input', {'id': 'account_number'}).get('value')	
                    incomingMsisdn[14] = soup.find('input', {'id': 'item_type'}).get('value')	
                    incomingMsisdn[15] = soup.find('input', {'id': 'production'}).get('value')	
                    incomingMsisdn[16] = soup.find('input', {'id': 'payment_type'}).get('value')						
                except:
                    pass				

                print ">>>>",nama_pelanggan_pln, daya_pln, client_ip, id_biller, systrace, inquiryid, billerid, biller_name, merchant_id, merchant_code, account_number, item_type, production, payment_type			
            else:				
                sendMessageT2(msisdn, "Nomor meter yang kamu masukkan tidak terdaftar atau salah, coba ulangi lagi ", 0)
                #answer = lineNlp.doNlp("ga jadi", msisdn, first_name)				
				
        if answer[:4] == "pl02":				
            sendRichCaptionT2(msisdn, 'https://www.bangjoni.com/line_images/payment_jatis1', answer[4:], 'jatis')	
            print incomingMsisdn[2]			
			
        if answer[:4] == "pl03":				
            params = {'id_biller': incomingMsisdn[5], 'payment_channel': incomingMsisdn[3], 'totalamount': int(incomingMsisdn[2]) + 2500}
            resp = requests.post('http://corepay.mobeli.co.id/jswitch/get_pg_amount2', data=params)	
            content = json.loads(resp.text)	
            x = content['pgamount']
            print incomingMsisdn[3], content['pgamount']	

            log_book(logDtm, msisdn, first_name, "PLN", incomingMsisdn[1] + "-" + incomingMsisdn[2])
            if incomingMsisdn[3] != "2": #NON ECASH PAYMENT
                #url_pay = 'http://128.199.88.72/pulsa/go_token1.php?totalamount=%s&payment_channel=%s&client_ip=%s&id_biller=%s&systrace=%s&inquiryid=%s&billerid=%s&biller_name=%s&merchant_id=%s&merchant_code=%s&account_number=%s&item_type=%s&production=%s&payment_type=%s&merchantamount=%s&pgamount=%s' % (int(incomingMsisdn[2]) + 2500, incomingMsisdn[3],incomingMsisdn[4],incomingMsisdn[5],incomingMsisdn[6],incomingMsisdn[7],incomingMsisdn[8],incomingMsisdn[9],incomingMsisdn[10],incomingMsisdn[11],incomingMsisdn[13],incomingMsisdn[14],incomingMsisdn[15],incomingMsisdn[16], int(incomingMsisdn[2]) + 2500, content['pgamount'])
                url_pay = 'http://128.199.139.105/pulsa/go_token2.php?msisdn=%s&p=token' % (msisdn)					
                url_post = 'totalamount=%s&payment_channel=%s&client_ip=%s&id_biller=%s&systrace=%s&inquiryid=%s&billerid=%s&biller_name=%s&merchant_id=%s&merchant_code=%s&account_number=%s&item_type=%s&production=%s&payment_type=%s&merchantamount=%s&pgamount=%s' % (int(incomingMsisdn[2]) + 2500, incomingMsisdn[3],incomingMsisdn[4],incomingMsisdn[5],incomingMsisdn[6],incomingMsisdn[7],incomingMsisdn[8],incomingMsisdn[9],incomingMsisdn[10],incomingMsisdn[11],incomingMsisdn[13],incomingMsisdn[14],incomingMsisdn[15],incomingMsisdn[16], int(incomingMsisdn[2]) + 2500, content['pgamount'])					
                lineNlp.redisconn.set(msisdn + "/token", url_post)												
                print url_pay
                sendLinkMessageT2(msisdn, 'berhasil pesen token listrik %s dengan harga %s (include biaya administrasi)' % (incomingMsisdn[2], x), 'DOKU Payment', 'Bayar Sekarang', url_pay, 'http://128.199.88.72/line_images/logobangjoni2.jpg')				
            else:
                params = {'totalamount': int(incomingMsisdn[2]) + 2500, 'payment_channel': incomingMsisdn[3], 'client_ip': incomingMsisdn[4], 'id_biller': incomingMsisdn[5], 'systrace': incomingMsisdn[6], 'inquiryid': incomingMsisdn[7], 'billerid': incomingMsisdn[8], 'biller_name': incomingMsisdn[9], 'merchant_id': incomingMsisdn[10], 'merchant_code': incomingMsisdn[11], 'account_number': incomingMsisdn[13], 'item_type': incomingMsisdn[14], 'production': incomingMsisdn[15], 'payment_type': incomingMsisdn[16], 'merchantamount': int(incomingMsisdn[2]) + 2500, 'pgamount': content['pgamount']}
                resp = requests.post('http://128.199.88.72/pulsa/go_token.php', data=params)	
                content = resp.text
                print content

                sqlstart = content.find("<REDIRECT>https://mandiriecash.com/ecommgateway")
                if sqlstart > -1:
                    url_pay = content[sqlstart+10:content.find("</REDIRECT>")]
                    print url_pay					
                    sendLinkMessageT2(msisdn, 'berhasil pesen token listrik %s dengan harga %s (include biaya administrasi)' % (incomingMsisdn[2], x), 'Mandiri eCash', 'Bayar Sekarang', url_pay, 'http://128.199.88.72/line_images/logobangjoni2.jpg')

            sql = "insert into jatis_billers values('" + incomingMsisdn[1] + "','" + msisdn + "','none','" + logDtm + "','" + incomingMsisdn[3] + "','')"
            print sql
            insert(sql)
				
            answer = lineNlp.doNlp("ga jadi", msisdn, first_name)	

####################TRANSLATOR START####################		
        if answer[:4] == "tr02":
            incomingMsisdn[1] = -1	
            sendMessageT2(msisdn, answer[5:], 0)

        if incomingMsisdn[1] == "TRANSLATOR_MODE":
            log_service(logDtm, msisdn, first_name, "TRANSLATOR", incomingMsisdn[2] + "-" + urllib.quote_plus(ask))		
            #incomingMsisdn[1] = -1
            print "http://127.0.0.1/translator/translate_bing.php?text=%s&lang=%s" % (urllib.quote_plus(ask), incomingMsisdn[2])
            respAPI = fetchHTML("http://127.0.0.1/translator/translate_bing.php?text=%s&lang=%s" % (urllib.quote_plus(ask), incomingMsisdn[2]))
            print respAPI
            sendMessageT2(msisdn, respAPI, 0)			
            #return			

        if answer[:4] == "tr01":
            log_service(logDtm, msisdn, first_name, "TRANSLATOR")				
            incomingMsisdn[1] = "TRANSLATOR_MODE"
            print "TRANSLATOR_MODE"
            #return



####################CHANGE CITY START####################
        if answer[:4] == "sc01":
            sql = "select * from reminder where msisdn = '%s' and is_prayer = 'No'" % (msisdn)
            print sql
            sqlout = request(sql)
            for row in sqlout:
                id, msisdn, dtm, once, is_prayer, is_day, description, name, platform, city, gmt = row
                GMT = (int(gmt) - int(incomingMsisdn[3]))
                date_object = datetime.strptime('%s' % (dtm), '%Y-%m-%d %H:%M:%S')
                NewlogDtm = (date_object + timedelta(hours=GMT)).strftime('%Y-%m-%d %H:%M:%S %A')
                sql = "update reminder set dtm = '%s %s', city = '%s', gmt = '%s' where msisdn = '%s' and description = '%s' and id = '%s' and is_prayer = 'No'" % (NewlogDtm.split(" ")[0], NewlogDtm.split(" ")[1], incomingMsisdn[2], incomingMsisdn[3], msisdn, description, id)
                print sql
                insert(sql)
				
####################REMINDER SHOLAT START####################
        if answer[:4] == "rs01" or answer[:4] == "sc01":
            log_service(logDtm, msisdn, first_name, "REMINDER SHOLAT", incomingMsisdn[2])		
            if answer[:4] == "sc01":
                incomingMsisdn[5] = incomingMsisdn[3]
                incomingMsisdn[3] = incomingMsisdn[2]      
            print "https://sholat.gq/adzan/monthly.php?id=%s" % (incomingMsisdn[4])
            #respAPI = fetchHTML("http://sholat.gq/adzan/monthly.php?id=%s" % (incomingMsisdn[4]))
            respAPI = fetchHTML("http://jadwalsholat.pkpu.or.id/monthly.php?id=%s" % (incomingMsisdn[4]))
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
                        insert("delete from reminder where msisdn = '%s' and is_prayer = 'Yes'" % (msisdn))
                        #islam_prayer = ['Imsyak','Shubuh','Terbit','Dhuha','Zhuhur','Ashr','Maghrib','Isya']
                        islam_prayer = ['Shubuh','Terbit','Dzuhur','Ashr','Maghrib','Isya']					
                        str = "Jadwal buka dan sholat %s hari ini:\n\n" % (incomingMsisdn[3])
                        i = status.find("<td>")
                        j = 0
                        while (i > -1):
                            str = str + islam_prayer[j] + " " + status[i+4:i+4+5] + "\n"

                            GMT = (7 - int(incomingMsisdn[5]))
                            date_object = datetime.strptime('1979-04-08 %s:00' % (status[i+4:i+4+5]), '%Y-%m-%d %H:%M:%S')
                            NewlogDtm = (date_object + timedelta(hours=GMT)).strftime('%Y-%m-%d %H:%M:%S %A')
                            if islam_prayer[j] != "Terbit" and islam_prayer[j] != "Dhuha" and islam_prayer[j] != "Imsyak":
                                sql = "insert into reminder values('" + logDtm.translate(None, ":- ") + "','" + msisdn + "','" + NewlogDtm.split(" ")[0] + " " + NewlogDtm.split(" ")[1] + "','No','Yes','Everyday','" + islam_prayer[j] + "','" + first_name + "','line','" + incomingMsisdn[3] + "','" + incomingMsisdn[5] + "')"
                                print sql
                                insert(sql)							
                            
                            status = status[14:]
                            j = j + 1
                            i = status.find("<td>")
                        print ">>> ", str
                        if answer[:4] == "rs01": sendMessageT2(msisdn, str, 0)		
		
		

####################REMINDER START####################
        if answer[:4] == "re01":
            log_service(logDtm, msisdn, first_name, "REMINDER", incomingMsisdn[6])		
            if incomingMsisdn[2] != "None" or incomingMsisdn[3] != "None" or incomingMsisdn[4] != "None":
                if incomingMsisdn[3] == "None":
                    incomingMsisdn[3] = "04:00:00"
                if incomingMsisdn[2] == "None":
                    incomingMsisdn[2] = "1979-08-04"
                GMT = (7 - int(incomingMsisdn[8]))
                date_object = datetime.strptime('%s %s' % (incomingMsisdn[2], incomingMsisdn[3]), '%Y-%m-%d %H:%M:%S')
                NewlogDtm = (date_object + timedelta(hours=GMT)).strftime('%Y-%m-%d %H:%M:%S %A')
                sql = "insert into reminder values('" + logDtm.translate(None, ":- ") + "','" + msisdn + "','" + NewlogDtm.split(" ")[0] + " " + NewlogDtm.split(" ")[1] + "','" + incomingMsisdn[5] + "','No','" + incomingMsisdn[4] + "','" + incomingMsisdn[6] + "','" + first_name + "','line','" + incomingMsisdn[7] + "','" + incomingMsisdn[8] + "')"
                print sql
                insert(sql)
            else:
                sendMessageT2(msisdn, lineNlp.doNlp("ingetin", msisdn, first_name), 0)             


####################INFO EURO 2016 START####################
        if answer[:4] == "eu01" or answer[:4] == "eu02":
            print "http://www.livescore.com/euro/fixtures/"
            respAPI = fetchHTML("http://www.livescore.com/euro/fixtures/")
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
                        delta = timedelta(hours=0)
                        target_date = date_select + delta
                        tgl_euro = target_date.strftime('%B %d')
                        ft_euro = target_date.strftime('%H:%M')
                    if ft_euro.find("&#x27;") > -1:
                        ft_euro = ft_euro.replace("&#x27;"," min (LIVE)")
                        print "------------------>", ft_euro
                    str = str + tgl_euro + " " + ft_euro + ":\n"
                    str = str + player_euro + " " + score_euro + "\n\n"
                    sqlstop = fixtures.find("match=")

                    if answer[:4] == "eu02" and player_euro.lower().find(incomingMsisdn[3]) > -1:
                        #print ">>", player_euro
                        str1 = str1 + tgl_euro + " " + ft_euro + ":\n"
                        str1 = str1 + player_euro + " " + score_euro + "\n"
                        player1 = player_euro.split("vs")[0]
                        player2 = player_euro.split("vs")[1]
                        print "http://www.livescore.com%s" % (url_player_euro)
                        respAPI = fetchHTML("http://www.livescore.com%s" % (url_player_euro))
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
                    sendMessageT2(msisdn, str, 0)
                else:
                    sendMessageT2(msisdn, str1, 0)
			
####################INFO EURO 2016 END##############

####################WAKTU SHOLAT####################
        if answer[:4] == "sh01":
            log_service(logDtm, msisdn, first_name, "SHOLAT", incomingMsisdn[3])		
            print "https://sholat.gq/adzan/monthly.php?id=%s" % (incomingMsisdn[4])
            #respAPI = fetchHTML("http://sholat.gq/adzan/monthly.php?id=%s" % (incomingMsisdn[4]))   
            respAPI = fetchHTML("http://jadwalsholat.pkpu.or.id/monthly.php?id=%s" % (incomingMsisdn[4]))
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
                        str = "Jadwal buka dan sholat %s hari ini:\n\n" % (incomingMsisdn[3])
                        i = status.find("<td>")
                        j = 0
                        while (i > -1):
                            str = str + islam_prayer[j] + " " + status[i+4:i+4+5] + "\n"
                            status = status[14:]
                            j = j + 1
                            i = status.find("<td>")
                        print ">>> ", str
                        sendMessageT2(msisdn, str, 0)						
                    
		
		
####################KASKUS####################
        if answer[:4] == "ka01":
            sendPhotoT2(msisdn, 'images/kaskus_movie.jpg', temp_answer, 0)
#################################################

####################LOG UNIDENTIFY USER RESPONSE####################
        if answer[:4] == "ee01" and incomingMsisdn[1] != "TRANSLATOR_MODE":
            #submit_unknown_agent(msisdn, ask, first_name)
            #sql = "insert into unknown_asking values('" + logDtm + "','" + msisdn + "','" + incomingMsisdn[27] + "','" + ask_temp + "','" + ask + "')"
            sql = logDtm + "," + msisdn + "," + first_name + "," + ask
            #insert(sql)   
            F_NOREPLY.info(sql)
        else:
            incomingMsisdn[27] = answer

####################CANCEL MODULE START####################
        if answer[:4] == "ca01":
            try:
                incomingMsisdn = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""]  
                bookingMsisdn = {}
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
            if answer[:4] == "ch02" and incomingMsisdn[6] != -1 and incomingMsisdn[7] != -1:
                print "http://128.199.88.72/uber/cancel_ride.php?request_id=%s&access_token=%s" % (incomingMsisdn[6], incomingMsisdn[7])
                respAPI = fetchHTML("http://128.199.88.72/uber/cancel_ride.php?request_id=%s&access_token=%s" % (incomingMsisdn[6], incomingMsisdn[7]))   
                print respAPI 

            incomingMsisdn = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""]             
###########################################################

####################INFO TOL MODULE FOR LOAD TEST START####################
        if answer[:4] == "xx01":
            log_service(logDtm, msisdn, first_name, "TOL LOAD TEST", incomingMsisdn[2])
            sql = "select * from tol_jasamarga where pintu = '%s'" % (incomingMsisdn[2])
            print sql
            sqlout = request(sql)
            ruas_tol = "";
            for row in sqlout:
                ruas_tol = row[0]

            if ruas_tol != "":
                print "http://127.0.0.1/twitter/jasamarga.php?ruas=%s&gate=%s" % (urllib.quote_plus(ruas_tol), urllib.quote_plus(incomingMsisdn[2]))
                respAPI = fetchHTML("http://127.0.0.1/twitter/jasamarga.php?ruas=%s&gate=%s" % (urllib.quote_plus(ruas_tol), urllib.quote_plus(incomingMsisdn[2])))
                #respAPI = "xxx"
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
                    sinfo_tol = "Dari Jasa marga, berikut info tol %s, jam %s WIB:" % (incomingMsisdn[2], jam_update)
                    #sendMessageT2(msisdn.decode('utf-8'), sinfo_tol + "\n" + s, 0)
                    lineNlp.redisconn.set(msisdn, sinfo_tol + "\n" + s)					

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
                            #sendPhotoT2(msisdn, '/tmp/' + item.split('/')[-1])
                else:
                    #sendMessageT2(msisdn, "Sorry " + first_name + ", Bang Joni belum update infonya, coba aja ruas tol lainnya", 0)
                    lineNlp.redisconn.set(msisdn, "Sorry " + first_name + ", Bang Joni belum update infonya, coba aja ruas tol lainnya")					


####################INFO TOL MODULE START####################
        if answer[:4] == "to01":
            log_service(logDtm, msisdn, first_name, "TOL", incomingMsisdn[2])
            sql = "select * from tol_jasamarga where pintu = '%s'" % (incomingMsisdn[2])
            print sql
            sqlout = request(sql)
            ruas_tol = "";
            for row in sqlout:
                ruas_tol = row[0]

            if ruas_tol != "":
                print "http://128.199.139.105/twitter/jasamarga.php?ruas=%s&gate=%s" % (urllib.quote_plus(ruas_tol), urllib.quote_plus(incomingMsisdn[2]))
                respAPI = fetchHTML("http://128.199.139.105/twitter/jasamarga.php?ruas=%s&gate=%s" % (urllib.quote_plus(ruas_tol), urllib.quote_plus(incomingMsisdn[2])))
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
                    sinfo_tol = "Dari Jasa marga, berikut info tol %s, jam %s WIB:" % (incomingMsisdn[2], jam_update)
                    sendMessageT2(msisdn.decode('utf-8'), sinfo_tol + "\n" + s, 0)

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
                            sendPhotoT2(msisdn, '/tmp/' + item.split('/')[-1])
                else:
                    sendMessageT2(msisdn, "Sorry " + first_name + ", Bang Joni belum update infonya, coba aja ruas tol lainnya", 0)

####################INFO TOL MODULE END####################

####################WEATHER MODULE START####################
        if answer[:4] == "we01":
            log_service(logDtm, msisdn, first_name, "CUACA")
            incomingMsisdn[11] = "we01"

        if ask[:5] == "[LOC]" and incomingMsisdn[11] == "we01":
            incomingMsisdn[11] == "";
            incomingMsisdn[2]  = ask[5:].split(';')[0]
            incomingMsisdn[3]  = ask[5:].split(';')[1]

            print "http://128.199.139.105/weather/weather1.php?latlong=%s,%s" % (incomingMsisdn[2], incomingMsisdn[3])
            respAPI = fetchHTML("http://128.199.139.105/weather/weather1.php?latlong=%s,%s" % (incomingMsisdn[2], incomingMsisdn[3]))
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
               print "*******************************"			   
               sendMessageT2(msisdn, first_name +  ", cuaca hari ini %s dengan suhu rata2 %s Celcius dan kecepatan angin %s Km/h.\nPerkiraan cuaca untuk besok adalah %s, dengan suhu minimal %s Celcius dan suhu maksimal %s Celcius" % (cuaca, suhu, kec_angin, tom_cuaca, tom_suhu_min, tom_suhu_max), 0)

####################WEATHER MODULE END####################


####################ZOMATO MODULE START####################
        if answer[:4] == "zo00":
            log_service(logDtm, msisdn, first_name, "ZOMATO")
            incomingMsisdn[11] = "zo00"

        if ask[:5] == "[LOC]" and incomingMsisdn[11] == "zo00":
            incomingMsisdn[11] == "";
            incomingMsisdn[2]  = ask[5:].split(';')[0]
            incomingMsisdn[3]  = ask[5:].split(';')[1]
            #sendMessageT2(msisdn, "Ok, Bang Joni sudah tahu lokasimu, sekarang kamu pingin masakan apa?", 0)
            #photo = open('/home/ubuntu/telegram/images/zomato_cuisines.png', 'rb')
            #sendPhotoT2(msisdn, 'images/zomato_cuisines.png')
            sendPhotoCaptionT2(msisdn, "https://www.bangjoni.com/line_images/zomato_cuisines.jpg", "https://www.bangjoni.com/line_images/zomato_cuisines.jpg", "Ok, Bang Joni sudah tahu lokasimu, sekarang kamu pingin masakan apa?")


        if answer[:4] == "zo01" or answer[:4] == "zo02":
            if answer[:4] == "zo01":
                print "http://128.199.139.105/zomato/search_restaurant.php?location=%s&cuisine=%s" % (incomingMsisdn[4], incomingMsisdn[3])
                respAPI = fetchHTML("http://128.199.139.105/zomato/search_restaurant.php?location=%s&cuisine=%s" % (incomingMsisdn[4], incomingMsisdn[3]))
            else:
                print "http://128.199.139.105/zomato/search_restaurant_longlat.php?long=%s&lat=%s&cuisines_id=%s" % (incomingMsisdn[3], incomingMsisdn[2], incomingMsisdn[4])
                respAPI = fetchHTML("http://128.199.139.105/zomato/search_restaurant_longlat.php?long=%s&lat=%s&cuisines_id=%s" % (incomingMsisdn[3], incomingMsisdn[2], incomingMsisdn[4]))
            print respAPI
            list_restaurants = ""
            sqlstart = respAPI.find("<found>")
            sqlstop = respAPI.find("</found>") - 1
            list_restaurants = respAPI[sqlstart+7:sqlstop]
            if list_restaurants != "":
                for item in list_restaurants.split(';'):
                    print item.split('|')[2]
                    #respAPI = fetchHTML(item.split('|')[2])
                    #print "---->", respAPI
                    #list_menu = ""
                    #sqlstart = respAPI.find("zomato.menuPages")
                    #sqlstop = respAPI.find("zomato.menuTypes") - 1
                    #list_menu = respAPI[sqlstart+16:sqlstop]
                    #if sqlstart != -1:
                        #jpg_menu = list_menu.split(',')[0].split(':')[2]
                        #jpg_menu = jpg_menu.translate(None, "\\\"")
                        #print jpg_menu
                        #print jpg_menu.split('/')[-1]
                    answer = item.split('|')[0] + "\n" + item.split('|')[1]
                    sendMessageT2(msisdn, answer, 0)
                        #f = open('/usr/share/nginx/html/line_images/' + jpg_menu.split('/')[-1],'wb')
                        #f.write(urllib.urlopen('https:' + jpg_menu).read())
                        #f.close()


                        #sendPhotoCaptionT2(msisdn, "http://128.199.88.72/line_images/%s" % (jpg_menu.split('/')[-1]), "http://128.199.88.72/line_images/%s" % (jpg_menu.split('/')[-1]), answer)
            else:
                sendMessageT2(msisdn, "Bang Joni tidak menemukan rekomendasi restoran dari zomato, coba cari tempat atau cuisine lainnya", 0)

####################ZOMATO MODULE END####################

####################XTRANS MODULE START####################
        if answer[:4] == "xt01":
            log_service(logDtm, msisdn, first_name, "XTRANS")
            sendPhotoCaptionT2(msisdn, 'http://128.199.88.72/line_images/Pool_Xtrans.jpg', 'http://128.199.88.72/line_images/Pool_Xtrans.jpg', answer.replace("xt01 ",""))
            incomingMsisdn[11] = "xt01"


        if answer[:4] == "xt02":
            incomingMsisdn[11] = "xt02"
            #if incomingMsisdn[3] == "semanggi": incomingMsisdn[3] = incomingMsisdn[3] + "/ kc"			
            sql = "select * from searching_xtrans where msisdn = '%s' and cabangtujuan ='%s'" % (msisdn, incomingMsisdn[3])
            print sql
            sqlout = request(sql)
            kode_jurusan = "";
            for row in sqlout:
                kode_jurusan = row[1]
                kota_asal = row[3]
                cabang_asal = row[4]
                kota_tujuan = row[5]
                cabang_tujuan = row[6]

            if kode_jurusan == "":
                answer = answer[4:] + "\n"
                #if incomingMsisdn[3] == "semanggi": incomingMsisdn[3] = incomingMsisdn[3] + "/ kc"
                print "http://128.199.139.105/tiketux/jurusan.php?d=%s" % (urllib.quote_plus(incomingMsisdn[3]))
                respAPI = fetchHTML("http://128.199.139.105/tiketux/jurusan.php?d=%s" % (urllib.quote_plus(incomingMsisdn[3])))
                print respAPI
                if len(respAPI) > 5:  
                    insert("delete from searching_xtrans where msisdn = '%s'" % (msisdn))
                    respAPI = respAPI[:len(respAPI)-1]
                    for cabangtujuan in respAPI.split('|'):
                        xtrans_id, xtrans_kode, xtrans_kotaAsal, xtrans_cabangAsal, xtrans_kotaTujuan, xtrans_cabangTujuan = cabangtujuan.split(';')
                        print xtrans_cabangTujuan
                        sql = "insert into searching_xtrans values('" + msisdn + "','" + xtrans_id + "','" + xtrans_kode + "','" + xtrans_kotaAsal + "','" + xtrans_cabangAsal.lower() + "','" + xtrans_kotaTujuan + "','" + xtrans_cabangTujuan.lower() + "')"
                        print sql
                        insert(sql)  
                        answer = answer + xtrans_cabangTujuan + "\n"
            else:
                insert("delete from searching_xtrans where msisdn = '%s'" % (msisdn))
                incomingMsisdn[3] = kode_jurusan
                incomingMsisdn[4] = kota_asal
                incomingMsisdn[5] = cabang_asal
                incomingMsisdn[6] = kota_tujuan
                incomingMsisdn[7] = cabang_tujuan
                ask = "xt02aa"
                answer = lineNlp.doNlp(ask, msisdn, first_name)

            sendMessageT2(msisdn, answer, 0)

        if answer[:4] == "xt03":
            incomingMsisdn[11] = ""
            ask = "xt03"
            answer = lineNlp.doNlp(ask, msisdn, first_name)   
            #sendMessageT2(msisdn, answer, 0)
            print "http://128.199.139.105/tiketux/jadwal_xtrans.php?jurusan=%s&tgl=%s&asal=%s&tujuan=%s" % (incomingMsisdn[3], incomingMsisdn[2], incomingMsisdn[5], incomingMsisdn[7])
            respAPI = fetchHTML("http://128.199.139.105/tiketux/jadwal_xtrans.php?jurusan=%s&tgl=%s&asal=%s&tujuan=%s" % (incomingMsisdn[3], incomingMsisdn[2], urllib.quote_plus(incomingMsisdn[5]), urllib.quote_plus(incomingMsisdn[7])))

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
                    randomDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y%m%d%H%M%S')	
                    pdf2jpg.write("%s_%s.jpg" % (outfile.split('.')[0], randomDtm))  
                    print "Done convert html to pdf to png"                                                
                    #photo = open('%s.jpg' % (outfile.split('.')[0]), 'rb')
                    #sendPhotoT2(msisdn, '%s.jpg' % (outfile.split('.')[0]))
                    sendPhotoCaptionT2(msisdn, 'http://128.199.88.72/line_images/%s_%s.jpg' % (outfile.split('.')[0].split('/')[6], randomDtm), 'http://128.199.88.72/line_images/%s_%s.jpg' % (outfile.split('.')[0].split('/')[6], randomDtm), answer)					

                    insert("delete from searching_jadwal_xtrans where msisdn = '%s'" % (msisdn))
                    list_airlines = list_airlines[:len(list_airlines)-1]
                    for cabangtujuan in list_airlines.split(','):
                        no, kode, jam_berangkat, layout_kursi, jumlah_kursi, jumlah_booking, harga = cabangtujuan.split(';')
                        sql = "insert into searching_jadwal_xtrans values('" + msisdn + "','" + no + "','" + kode + "','" + jam_berangkat + "','" + layout_kursi + "','" + jumlah_kursi + "','" + jumlah_kursi + "','" + harga + "')"
                        #print sql
                        insert(sql)   
            else:
                sendMessageT2(msisdn, "Bang Joni tidak menemukan jadwalnya, coba cari tanggal lainnya...", 0)

        if answer[:4] == "xt04":
            incomingMsisdn[11] = ""
            answer = answer + "\n%s penumpang dengan format: " % (incomingMsisdn[1])
            for i in range(incomingMsisdn[1]):
                answer = answer + "nama lengkap " + `i+1` + ","
            answer = answer[:len(answer)-1]
            sendMessageT2(msisdn, answer.replace('xt04 ',''), 0)

            
        if answer[:4] == "xt06":
            incomingMsisdn[11] = ""
            answertemp = answer
            ask = "xt06aa"
            answer = lineNlp.doNlp(ask, msisdn, first_name)
            sql = "select * from searching_jadwal_xtrans where msisdn = '%s' and no = %s" % (msisdn, incomingMsisdn[10])
            print sql
            sqlout = request(sql)
            kode = ""
            for row in sqlout:
                kode = row[2]
                layout_kursi = row[4]
            if kode != "":
                incomingMsisdn[4] = kode
                incomingMsisdn[6] = layout_kursi

            print "http://128.199.139.105/tiketux/layout_kursi.php?kode=%s&tgl=%s&jadwal=%s" % (incomingMsisdn[6], incomingMsisdn[2], incomingMsisdn[4])
            respAPI = fetchHTML("http://128.199.139.105/tiketux/layout_kursi.php?kode=%s&tgl=%s&jadwal=%s" % (incomingMsisdn[6], incomingMsisdn[2], incomingMsisdn[4]))
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
                    randomDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y%m%d%H%M%S')	
                    pdf2jpg.write("%s_%s.jpg" % (outfile.split('.')[0], randomDtm))  
                    print "Done convert html to pdf to png"                                                
                    #photo = open('%s.jpg' % (outfile.split('.')[0]), 'rb')
                    #sendPhotoT2(msisdn, '%s.jpg' % (outfile.split('.')[0]))
                    sendPhotoCaptionT2(msisdn, 'http://128.199.88.72/line_images/%s_%s.jpg' % (outfile.split('.')[0].split('/')[6], randomDtm), 'http://128.199.88.72/line_images/%s_%s.jpg' % (outfile.split('.')[0].split('/')[6], randomDtm), answertemp.replace("xt06 ",""))

        if answer[:4] == "xt09": 
            log_book(logDtm, msisdn, first_name, "XTRANS", incomingMsisdn[4] + "-" + incomingMsisdn[2])		
            incomingMsisdn[11] = ""
            print "--------------> ",incomingMsisdn[3]
            #print "http://128.199.139.105/tiketux/booking.php?jadwal=%s&tanggal_berangkat=%s&nomor_kursi=%s&nama_penumpang=%s&nama_pemesan=%s&alamat_pemesan=%s&telp_pemesan=%s&email_pemesan=%s&channel=BGJ&payment=fin195" % (incomingMsisdn[4], incomingMsisdn[2], urllib.quote_plus(incomingMsisdn[3]), urllib.quote_plus(incomingMsisdn[9]), urllib.quote_plus('elina wardhani'), urllib.quote_plus('cibubur bogor'), urllib.quote_plus('08119772759'), urllib.quote_plus(EMAIL_NOTIF))
            #respAPI = fetchHTML("http://128.199.139.105/tiketux/booking.php?jadwal=%s&tanggal_berangkat=%s&nomor_kursi=%s&nama_penumpang=%s&nama_pemesan=%s&alamat_pemesan=%s&telp_pemesan=%s&email_pemesan=%s&channel=BGJ&payment=fin195" % (incomingMsisdn[4], incomingMsisdn[2], incomingMsisdn[3], urllib.quote_plus(incomingMsisdn[9]), urllib.quote_plus('elina wardhani'), urllib.quote_plus('cibubur bogor'), urllib.quote_plus('08119772759'), urllib.quote_plus(EMAIL_NOTIF)))
            print "http://128.199.139.105/tiketux/booking1.php?jadwal=%s&tanggal_berangkat=%s&nomor_kursi=%s&nama_penumpang=%s&nama_pemesan=%s&alamat_pemesan=%s&telp_pemesan=%s&email_pemesan=%s&channel=BGJ&payment=%s" % (incomingMsisdn[4], incomingMsisdn[2], urllib.quote_plus(incomingMsisdn[3]), urllib.quote_plus(incomingMsisdn[9]), urllib.quote_plus(incomingMsisdn[9].split(",")[0]), urllib.quote_plus('Bang Joni, Palma One 2nd floor suit 210 Jakarta Selatan'), urllib.quote_plus(incomingMsisdn[7]), urllib.quote_plus(EMAIL_NOTIF), incomingMsisdn[5])
            respAPI = fetchHTML("http://128.199.139.105/tiketux/booking1.php?jadwal=%s&tanggal_berangkat=%s&nomor_kursi=%s&nama_penumpang=%s&nama_pemesan=%s&alamat_pemesan=%s&telp_pemesan=%s&email_pemesan=%s&channel=BGJ&payment=%s" % (incomingMsisdn[4], incomingMsisdn[2], incomingMsisdn[3], urllib.quote_plus(incomingMsisdn[9]), urllib.quote_plus(incomingMsisdn[9].split(",")[0]), urllib.quote_plus('Bang Joni, Palma One 2nd floor suit 210 Jakarta Selatan'), urllib.quote_plus(incomingMsisdn[7]), urllib.quote_plus(EMAIL_NOTIF), incomingMsisdn[5]))			
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
                answer = lineNlp.doNlp(ask, msisdn, first_name)
                sql = "insert into booking_xtrans values('%s','%s','%s','%s')" % (msisdn, logDtm, kodeBooking, kodePembayaran)                                      
                print ">>", sql
                insert(sql)

                sql = "select * from searching_jadwal_xtrans where msisdn = '%s' and no = %s" % (msisdn, incomingMsisdn[10])
                print sql
                sqlout = request(sql)
                harga = "0"
                for row in sqlout: 
                    print "--->", incomingMsisdn[1], row[7]
                    x = int(row[7].replace(".","")) * int(incomingMsisdn[1])
                    harga = '{0:,}'.format(x)
                    harga = harga.replace(",",".")

                if incomingMsisdn[5] == "fin195":
                    sendMessageT2(msisdn, "Bang Joni sudah berhasil booking pesananmu, berikut detailnya:\nKode Booking: %s\nKode Pembayaran: %s\nJumlah Pembayaran: Rp. %s\nLakukan pembayaran via ATM secepatnya sebelum %s agar tiket kamu tidak dibatalkan.\nBang Joni akan kirim tiket jika pembayaran telah diterima." % (kodeBooking, kodePembayaran, harga, batasPembayaran), 0)
                    sendPhotoT2(msisdn, '/usr/share/nginx/html/line_images/tiketux_atm.jpg')
                elif incomingMsisdn[5] == "indomaret":
                    sendMessageT2(msisdn, "Bang Joni sudah berhasil booking pesananmu, berikut detailnya:\nKode Booking: %s\nKode Pembayaran: %s\nJumlah Pembayaran: Rp. %s\nLakukan pembayaran ke Indomaret terdekat secepatnya sebelum %s agar tiket kamu tidak dibatalkan.\nBang Joni akan kirim tiket jika pembayaran telah diterima." % (kodeBooking, kodePembayaran, harga, batasPembayaran), 0)										
                else:
                    print "Bang Joni sudah berhasil booking pesananmu, berikut detailnya:\nKode Booking: %s\nKode Pembayaran: %s\nJumlah Pembayaran: Rp. %s\nLakukan pembayaran via %s dengan cara <a href=\"%s\">click disini</a> sebelum %s agar tiket kamu tidak dibatalkan.\nBang Joni akan kirim tiket jika pembayaran telah diterima." % (kodeBooking, kodePembayaran, harga, incomingMsisdn[8], url_pay, batasPembayaran)
                    #sendMessageT2(msisdn, "Bang Joni sudah berhasil booking pesananmu, berikut detailnya:\nKode Booking: %s\nKode Pembayaran: %s\nJumlah Pembayaran: Rp. %s\nLakukan pembayaran via %s dengan cara <a href=\"%s\">click disini</a> sebelum %s agar tiket kamu tidak dibatalkan.\nBang Joni akan kirim tiket jika pembayaran telah diterima." % (kodeBooking, kodePembayaran, harga, incomingMsisdn[8], url_pay, batasPembayaran), 0)
                    sendLinkMessageT2(msisdn, 'berhasil booking, detailnya:\nKode Booking: %s\nKode Pembayaran: %s\nHarga: Rp. %s\nLakukan pembayaran sebelum %s.\nBang Joni kirim tiket jika pembayaran diterima' % (kodeBooking, kodePembayaran, harga, batasPembayaran), incomingMsisdn[8], 'Bayar Sekarang', url_pay, 'http://128.199.88.72/line_images/logobangjoni2.jpg')					
					
            if len(errormsg) > 2:
                sendMessageT2(msisdn, "Bang joni dapat info dari xtrans: %s" % (errormsg), 0)
                #sendMessageT2(msisdn, "Pilih kursi yang kosong aja ya..", 0)

            
####################XTRANS MODULE END####################

####################UBER MODULE START####################
        if answer[:4] == "ub01":
            log_service(logDtm, msisdn, first_name, "UBER")
            incomingMsisdn[11] = "ub01"
            incomingMsisdn[2] = -1
            sql = "select * from token_uber where msisdn = '%s'" % (msisdn)
            print sql
            sqlout = request(sql)
            token_uber = ""
            for row in sqlout:
                token_uber = row[2]
            if token_uber == "" or token_uber == "X":
                credentials = import_app_credentials()
                incomingMsisdn[1] = AuthorizationCodeGrant(
                    credentials.get('client_id'),
                    credentials.get('scopes'),
                    credentials.get('client_secret'),
                    credentials.get('redirect_url'),
                )
                print "---------->>>>>>>>>>>",incomingMsisdn[1] 
                auth_url = incomingMsisdn[1].get_authorization_url()
                state = auth_url.split('&')[1].split('=')[1]
                print ">>>>", auth_url, state
                insert("delete from token_uber where msisdn = '%s'" % (msisdn))
                #sql = "insert into token_uber(msisdn, state, access_token, platform, AuthorizationCodeGrant) values('" + msisdn + "','" + state + "','X','line','" + incomingMsisdn[1] + "')"
                sql = "insert into token_uber(msisdn, state, access_token, platform) values('" + msisdn + "','" + state + "','X','line')"
                insert(sql)  
                incomingMsisdn[1] = pickle.dumps(incomingMsisdn[1])

                answer = "Bang Joni belum terhubung dengan account Ubermu\n"
                answer = answer + "Untuk memberikan ijin Bang Joni terhubung account Ubermu <a href=\"" + auth_url + "\">click disini</a> ya"
                #answer = answer + "Click url berikut untuk memberikan ijin BangJoni menggunakan uber accountmu:\n"
                #answer = answer + auth_url
                #sendMessageT2(msisdn, answer, 0)
                sendLinkMessageT2(msisdn, 'belum terhubung dengan account Ubermu\nUntuk memberikan ijin Bang Joni terhubung account Ubermu tap Ijin Uber', 'Uber', 'Ijin Uber', auth_url, 'http://128.199.88.72/line_images/uber.JPG')				
            else:
                #answer = "Share lokasimu dengan cara click tombol PIN dan tap Location"
                answer = "Mau naik uberX atau uberMotor?"						
                sendMessageT2(msisdn, answer, 0)
        
        if ask[:5] == "[LOC]" and incomingMsisdn[11] == "ub01":
            incomingMsisdn[11] = "ub01"
            if incomingMsisdn[2] == -1:
               incomingMsisdn[2]  = ask[5:].split(';')[0]
               incomingMsisdn[3]  = ask[5:].split(';')[1]
               sendMessageT2(msisdn, "Sekarang share lokasi tujuanmu dengan cara click tombol + sebelah tombol smile dan tap Share Location", 0)
            elif incomingMsisdn[2] != -1:
               answer = lineNlp.doNlp("ub02", msisdn, first_name)
               incomingMsisdn = json.loads(lineNlp.redisconn.get("inc/%s" % (msisdn)))			   
               #sendMessageT2(msisdn, answer, 0)
               print ">>>>", incomingMsisdn
               incomingMsisdn[4]  = ask[5:].split(';')[0]
               incomingMsisdn[5]  = ask[5:].split(';')[1]
               sql = "select * from token_uber where msisdn = '%s'" % (msisdn)
               print sql
               sqlout = request(sql)
               access_token = ""
               refresh_token = ""	
               for row in sqlout:
                   access_token = row[2]
                   refresh_token = row[1]	
               if access_token != "":	   
                   incomingMsisdn[8] = access_token				   
                   incomingMsisdn[9] = refresh_token				   
                   print "http://128.199.88.72/uber/estimate_price.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&refresh_token=%s&product=%s" % (incomingMsisdn[2], incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[5], access_token, refresh_token, incomingMsisdn[6])
                   respAPI = fetchHTML("http://128.199.88.72/uber/estimate_price.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&refresh_token=%s&product=%s" % (incomingMsisdn[2], incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[5], access_token, refresh_token, incomingMsisdn[6]))   
                   print "REQUEST_RIDE:", respAPI			   
                   sqlstart = respAPI.find("access_token")
                   if sqlstart > -1:	
                       new_access_token = ""
                       new_refresh_token = ""
                       new_expires_in = ""				
					   
                       content = json.loads(respAPI)
                       print ">>>>>",content
                       new_access_token = content['access_token']		
                       new_refresh_token = content['refresh_token']				
                       new_expires_in = content['expires_in']		
                       access_token = new_access_token	
                       refresh_token = new_refresh_token				   
                       incomingMsisdn[8] = new_access_token				   
                       incomingMsisdn[9] = new_refresh_token				   					   
			   
                       sql = "update token_uber set access_token='%s', refresh_token='%s', expires_in_sec='%s' where msisdn='%s'" % (new_access_token, new_refresh_token, new_expires_in, msisdn)
                       print sql
                       insert(sql)  
					   
                       sql = "select * from token_uber where msisdn = '%s'" % (msisdn)
                       print sql
                       sqlout = request(sql)
                       email = ""
                       for row in sqlout:
                           email = row[6]
                       if email != "":
                           sql = "update token_uber set access_token='%s', refresh_token='%s', expires_in_sec='%s' where email='%s'" % (new_access_token, new_refresh_token, new_expires_in, email)
                           print sql
                           insert(sql)  				   

                       print "http://128.199.88.72/uber/estimate_price.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&refresh_token=%s&product=%s" % (incomingMsisdn[2], incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[5], access_token, refresh_token, incomingMsisdn[6])
                       respAPI = fetchHTML("http://128.199.88.72/uber/estimate_price.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&refresh_token=%s&product=%s" % (incomingMsisdn[2], incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[5], access_token, refresh_token, incomingMsisdn[6]))   
                       print "REQUEST_RIDE_NEW_TOKEN:", respAPI							   

                   sqlstart = respAPI.find("<estimate>")
                   sqlstop = respAPI.find("</estimate>")
                   if sqlstart > -1:
                       estimate_price = respAPI[sqlstart+10:sqlstop]
                       sqlstart = respAPI.find("<distance>")
                       sqlstop = respAPI.find("</distance>")
                       distance = respAPI[sqlstart+10:sqlstop]   
                       sqlstart = respAPI.find("<surge_multiplier>")
                       sqlstop = respAPI.find("</surge_multiplier>")
                       surge_multiplier = respAPI[sqlstart+18:sqlstop]
                       if surge_multiplier == "1":
                           sendMessageT2(msisdn, "Bang Joni dapat %s dengan estimasi harga %s dan jauh perjalanan %s km\nMau lanjut? (ok/cancel)" % (incomingMsisdn[6], estimate_price, distance), 0)
                       else:		
                           sendMessageT2(msisdn, "Waktu peak, bang Joni dapat %s dengan estimasi harga %s, naik %s kali lapat dengan jauh perjalanan %s km\nMau lanjut? (ok/cancel)" % (incomingMsisdn[6], estimate_price, surge_multiplier, distance), 0)
                   else:
                       x = "uberX"	   
                       if incomingMsisdn[6] == "uberX": x = "uberMotor"
                       if incomingMsisdn[6] == "uberMotor": x = "uberX"		
                       incomingMsisdn[6] = x					   
                       
                       print "http://128.199.88.72/uber/estimate_price.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&refresh_token=%s&product=%s" % (incomingMsisdn[2], incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[5], access_token, refresh_token, x)
                       respAPI = fetchHTML("http://128.199.88.72/uber/estimate_price.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&refresh_token=%s&product=%s" % (incomingMsisdn[2], incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[5], access_token, refresh_token, x))   
                       print "REQUEST_RIDE_OTHERS:", respAPI							   

                       sqlstart = respAPI.find("<estimate>")
                       sqlstop = respAPI.find("</estimate>")
                       if sqlstart > -1:
                           estimate_price = respAPI[sqlstart+10:sqlstop]
                           sqlstart = respAPI.find("<distance>")
                           sqlstop = respAPI.find("</distance>")
                           distance = respAPI[sqlstart+10:sqlstop]   
                           sqlstart = respAPI.find("<surge_multiplier>")
                           sqlstop = respAPI.find("</surge_multiplier>")
                           surge_multiplier = respAPI[sqlstart+18:sqlstop]
                           if surge_multiplier == "1":
                               sendMessageT2(msisdn, "%s nggak ada di sekitarmu, bang joni dapat %s dengan estimasi harga %s dan jauh perjalanan %s km\nMau lanjut? (ok/cancel)" % (incomingMsisdn[6], x, estimate_price, distance), 0)
                           else:		
                               sendMessageT2(msisdn, "Waktu peak, %s nggak ada di sekitarmu, bang Joni dapat %s dengan estimasi harga %s, naik %s kali lapat dengan jauh perjalanan %s km\nMau lanjut? (ok/cancel)" % (incomingMsisdn[6], x, estimate_price, surge_multiplier, distance), 0) 
                       else:
                           # respAPIJson = json.loads(respAPI)
                           # print respAPIJson["message"]
                           if (respAPI.find("No authentication provided") > 1 and respAPI.find("invalid_grant") > 1):
                               print "kayanya token kamu udah abis, coba ulangi lagi"
                               insert("delete from token_uber where msisdn = '%s'" % (msisdn))
                               credentials = import_app_credentials()
                               incomingMsisdn[1] = AuthorizationCodeGrant(
                                   credentials.get('client_id'),
                                   credentials.get('scopes'),
                                   credentials.get('client_secret'),
                                   credentials.get('redirect_url'),
                               )
                               auth_url = incomingMsisdn[1].get_authorization_url()
                               sendLinkMessageT2(msisdn, 'belum terhubung dengan account Ubermu\nUntuk memberikan ijin Bang Joni terhubung account Ubermu tap Ijin Uber', 'Uber', 'Ijin Uber', auth_url, 'http://128.199.88.72/line_images/uber.JPG')
                           else :
                               sendMessageT2(msisdn, "Bang Joni nggak dapat %s, coba ulangi dari awal ya..." % (incomingMsisdn[6]), 0)
                               answer = lineNlp.doNlp("exittorandom", msisdn, first_name)

        if answer[:4] == "ub03":
            access_token = incomingMsisdn[8]	
            print "http://128.199.88.72/uber/check_payment.php?access_token=%s" % (access_token)
            respAPI = fetchHTML("http://128.199.88.72/uber/check_payment.php?access_token=%s" % (access_token))   
            print "REQUEST_RIDE_LIST_PAYMENTS:", respAPI
            sqlstart = respAPI.find("<payments>")
            sqlstop = respAPI.find("</payments>")
            if sqlstart > -1:
                incomingMsisdn[7] = respAPI[sqlstart+10:sqlstop]
                incomingMsisdn[7] = incomingMsisdn[7][:-1]				
                answer = ""				
                for subitem in incomingMsisdn[7].split(';'):
                    answer = answer + subitem.split('|')[0] + " atau "
                answer = answer[:-6] + "?"					
                sendMessageT2(msisdn, answer, 0)  
            else: sendMessageT2(msisdn, "Bang Joni nggak dapat response dari Uber, ketik cancel untuk ulang", 0) 				

        if answer[:4] == "ub04":
            access_token = incomingMsisdn[8]	
            refresh_token = incomingMsisdn[9]				
            payment_method_id = ""
            for subitem in incomingMsisdn[7].split(';'):	
               if subitem.split('|')[0] == incomingMsisdn[10]: payment_method_id = subitem.split('|')[1]
            if payment_method_id != "":   
  
                print "http://128.199.88.72/uber/request_ride.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&refresh_token=%s&product=%s&payment_method_id=%s" % (incomingMsisdn[2], incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[5], access_token, refresh_token, incomingMsisdn[6], payment_method_id)
                respAPI = fetchHTML("http://128.199.88.72/uber/request_ride.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&refresh_token=%s&product=%s&payment_method_id=%s" % (incomingMsisdn[2], incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[5], access_token, refresh_token, incomingMsisdn[6], payment_method_id))   
                print "REQUEST_RIDE:", respAPI
				   
                request_id = ""
                status = ""
                sqlstart = respAPI.find("<status>")
                sqlstop = respAPI.find("</status>")
                status = respAPI[sqlstart+8:sqlstop]   
                sqlstart = respAPI.find("<request_id>")
                sqlstop = respAPI.find("</request_id>")
                request_id = respAPI[sqlstart+12:sqlstop]
   
                if sqlstart > -1:
                    incomingMsisdn[6] = request_id
                    incomingMsisdn[7] = access_token
                    #insert("delete from booking_uber where msisdn = '%s'" % (msisdn))
                    sql = "insert into booking_uber values('" + msisdn + "','" + first_name + "','" + request_id + "','" + status + "','" + logDtm +  "','" + access_token + "','line')"
                    print sql
                    insert(sql)
                    incomingMsisdn[11] = ""
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
                        insert(sql)
                        answer = first_name + ", jam sekarang Uber lagi penuh, naik " + multiplier + " kali lipat tarif normal, jika tetep order, <a href=\"" + surge + "\">click disini</a>"
                        #answer = answer + surge
                        #sendMessageT2(msisdn, answer, 0)
                        sendLinkMessageT2(msisdn, "dapat info Uber jam sekarang lagi penuh, naik " + multiplier + " kali lipat tarif normal, jika tetep order", 'Uber', 'Tetap Pesan', surge, 'http://128.199.88.72/line_images/uber.JPG')					
                    else:
                        sendMessageT2(msisdn, "Bang Joni, nggak dapat response dari Uber, coba lagi ya...", 0)
            else: sendMessageT2(msisdn, "Bang Joni nggak dapat response dari Uber, ketik cancel untuk ulang", 0) 				
			
			
####################TRAIN MODULE START####################
        if answer[:4] == "ke00":
            log_service(logDtm, msisdn, first_name, "TRAIN")
            incomingMsisdn[11] = "ke00"
            print "*******************************>"

        if answer[:4] == "ke01":
            incomingMsisdn[11] = "ke00"
            #calling kereta api API
            ask = "ke01"
            answer = lineNlp.doNlp(ask, msisdn, first_name)   
            sendMessageT2(msisdn, answer, 0)
            print "http://128.199.139.105/train/cari_train1.php?d=%s&a=%s&roundtrip=1&adult=%d&infant=%d&date=%s&ret_date=" % (incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[9], incomingMsisdn[10], incomingMsisdn[2])
            respAPI = fetchHTML("http://128.199.139.105/train/cari_train1.php?d=%s&a=%s&roundtrip=1&adult=%d&infant=%d&date=%s&ret_date=" % (incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[9], incomingMsisdn[10], incomingMsisdn[2]))

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

                    #goHtml2Png(respAPI, msisdn)
                    print "Done convert html to pdf to png"                                                
                    #photo = open('%s.jpg' % (outfile.split('.')[0]), 'rb')
                    sendPhotoT2(msisdn, '%s.jpg' % (outfile.split('.')[0]))

                    incomingMsisdn[13] = token                                          
                    insert("delete from searching_train where msisdn = '%s'" % (msisdn))
                    for item in list_airlines.split(';'):
                        sql = "insert into searching_train values('" + msisdn + "','" + incomingMsisdn[2] + "',"
                        for sub_item in item.split('|'):
                            sql = sql + "'" + sub_item + "',"
                        if sub_item:
                            sql = sql + "'" + token + "')"   
                            print sql                                                     
                            insert(sql)  

            else:
                answer = "Bang Joni tidak menemukan kereta yang available. Coba tanggal atau rute lainnya."                    
                sendMessageT2(msisdn, answer, 0)
                incomingMsisdn[14] = -1   
                incomingMsisdn[15] = 2  

        if answer[:4] == "ke02":
            #calling kereta api API
            if incomingMsisdn[9] > 0 and incomingMsisdn[10] == 0:
                answer = "%d dewasa diatas 2 tahun dengan format: (Tn/Ny/Nona);nama lengkap;KTP" % (incomingMsisdn[9])
            if incomingMsisdn[9] > 0 and incomingMsisdn[10] > 0:
                answer = "%d dewasa diatas 2 tahun dan %d bayi dengan format: (d=dewasa/b=bayi);(Tn/Ny/Nona);nama lengkap;KTP" % (incomingMsisdn[9], incomingMsisdn[10])
            sendMessageT2(msisdn, answer, 0)

        if answer[:4] == "ke04":
            #calling kereta api API
            ask = "ke04aa"
            print "AAAAAAAAAAAAAAAAAAAA"
            answer = lineNlp.doNlp(ask, msisdn, first_name)
            print "BBBBBBBBBBBBBBBBBBBB"
            print bookingMsisdn        
            incomingMsisdn[14] = 1                    
            s = ""                    
            logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')   
            
            sql = "select * from searching_train where msisdn = '%s' and id = %s" % (msisdn, bookingMsisdn['train_id'])
            print sql
            sqlout = request(sql)
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
                 bookingMsisdn['d'] = dep_station
                 bookingMsisdn['a'] = arr_station
                 bookingMsisdn['date'] = departure_date
                 bookingMsisdn['token'] = token
                 bookingMsisdn['subclass'] = subclass
                 bookingMsisdn['train_id'] = train_id
                 log_book(logDtm, msisdn, first_name, "XTRANS", departure_date + "-" + dep_station + "-" + arr_station)						 
            
                 for key in bookingMsisdn:
                     s = s + key + "=" + bookingMsisdn[key] + "&"                                                              
                 bookingMsisdn['train_name'] = train_name 
                 s = s + "x=1"               
                 s = "http://128.199.139.105/train/order_wh_train.php?" + s    
                 print s
                 respAPI = fetchHTML(s)   
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

                        #goHtml2Png(respAPI, msisdn)
                        print "Done convert html to pdf to png"                                                
                        #photo = open('%s.jpg' % (outfile.split('.')[0]), 'rb')
                        sendPhotoT2(msisdn, '%s.jpg' % (outfile.split('.')[0]))
                         
                        sqlstart = respAPI.find("<TOKEN>")
                        sqlstop = respAPI.find("</TOKEN>")
                        token = respAPI[sqlstart+7:sqlstop]   
                        sqlstart = respAPI.find("<ORDERID>")
                        sqlstop = respAPI.find("</ORDERID>")
                        orderid = respAPI[sqlstart+9:sqlstop]    

                        
                         
                        sql = "insert into booking_train values('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (logDtm, msisdn, bookingMsisdn['date'], bookingMsisdn['train_id'], bookingMsisdn['train_name'], bookingMsisdn['a'], bookingMsisdn['d'], orderid, token )                                      
                        print ">>", sql
                        insert(sql)                                                
                        time.sleep(5)

                        s = "http://128.199.139.105/train/bayar_wh_train.php?token=%s&orderid=%s&title=%s&first_name=%s&email=%s&phone=%s" % (token, orderid, bookingMsisdn['conSalutation'], bookingMsisdn['conFirstName'], bookingMsisdn['conEmailAddress'], bookingMsisdn['conPhone'])                         
                        print s                         
                        respAPI = fetchHTML(s)  
                        if respAPI.find("ATM_SUKSES") >= 0:    
                            #goHtml2Png(respAPI, msisdn + "_bayar")
                            #print "Done convert html to png"    
                            incomingMsisdn = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""]  
                            bookingMsisdn = {}                              
                            #sendImg("/tmp/%s_bayar.jpg" %(msisdn), msisdn)
                            print "Sukses ATM:"
                        else: 
                            print "Bayar error:", respAPI
                            answer = "Maaf, order pembayaran via ATM tdk bisa, ulangi lagi ya..."
                            err_msg = respAPI[respAPI.find("error_msgs")+10:respAPI.find("status")]   
                            err_msg = err_msg.translate(None, ",'!.?$%:\"")
                            #try:
                                #sql = "insert into booking_error values('%s','%s','%s','%s','%s')" % (logDtm, msisdn, incomingMsisdn[13], s, err_msg)                                      
                                #insert(sql)  
                            #except:
                                #print "sql error at order gopegi"  
                            answer = answer + ": " + err_msg
                            sendMessageT2(msisdn, answer, 0)
                        try:
                            incomingMsisdn = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""]  
                            bookingMsisdn = {}
                        except Exception as e:
                            return 1
####################TRAIN MODULE END####################

####################FLIGHT MODULE END####################
        if answer[:4] == "fl01":
            log_service(logDtm, msisdn, first_name, "FLIGHT")
            incomingMsisdn[14] = 1
            incomingMsisdn[15] = 2
                    
            print "http://128.199.88.72/flight/cari_whx_line.php?asal=%s&tujuan=%s&roundtrip=1&dewasa=%d&anak=%d&bayi=%d&pergi=%s&airline=%s&waktu=%s&transit=%s&pulang=" % (incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[9], incomingMsisdn[10], incomingMsisdn[11], incomingMsisdn[2], incomingMsisdn[8], incomingMsisdn[23], incomingMsisdn[24])
            respAPI = fetchHTML("http://128.199.88.72/flight/cari_whx_line.php?asal=%s&tujuan=%s&roundtrip=1&dewasa=%d&anak=%d&bayi=%d&pergi=%s&airline=%s&waktu=%s&transit=%s&pulang=" % (incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[9], incomingMsisdn[10], incomingMsisdn[11], incomingMsisdn[2], incomingMsisdn[8], incomingMsisdn[23], incomingMsisdn[24]))
            print "----->", respAPI                      
            sqlstart = respAPI.find("<TOKEN>")
            sqlstop = respAPI.find("</TOKEN>")
            token = respAPI[sqlstart+7:sqlstop]
      

            sqlstart = respAPI.find("<SQL>")
            sqlstop = respAPI.find("</SQL>")
            list_airlines = respAPI[sqlstart+5:sqlstop]
            insert("insert into searched_tickets values ('" + logDtm + "','" + msisdn + "','" + incomingMsisdn[3] + "','" + incomingMsisdn[4] + "','" + incomingMsisdn[8] + "','" + incomingMsisdn[2] + "')")                        
            incomingMsisdn[21] = incomingMsisdn[3]                    
            incomingMsisdn[22] = incomingMsisdn[4]                    

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
                    answer = lineNlp.doNlp(ask, msisdn, first_name)
                    #sendMessageT2(msisdn, answer, 0)

                    outfile = '/usr/share/nginx/html/line_images/%s_cari.pdf' % (msisdn)
                    pdf2jpg = PythonMagick.Image()
                    pdf2jpg.density("200")
                    pdf2jpg.read(outfile)
                    randomDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y%m%d%H%M%S')	
                    pdf2jpg.write("%s_%s.jpg" % (outfile.split('.')[0], randomDtm))  

                    #goHtml2Png(respAPI, msisdn)
                    print "Done convert html to pdf to png %s_%s.jpg" % (outfile.split('.')[0].split('/')[6], randomDtm)                                                
                    #photo = open('%s.jpg' % (outfile.split('.')[0]), 'rb')
                    #sendPhotoT2(msisdn, '%s.jpg' % (outfile.split('.')[0]))
                    sendPhotoCaptionT2(msisdn, 'http://128.199.88.72/line_images/%s_%s.jpg' % (outfile.split('.')[0].split('/')[6], randomDtm), 'http://128.199.88.72/line_images/%s_%s.jpg' % (outfile.split('.')[0].split('/')[6], randomDtm), answer)

					
                    incomingMsisdn[13] = token                                          
                    insert("delete from searching_airlines where msisdn = '%s'" % (msisdn))
                    for item in list_airlines.split(';'):
                        sql = "insert into searching_airlines values('" + msisdn + "','" + incomingMsisdn[2] + "',"
                        for sub_item in item.split('|'):
                            sql = sql + "'" + sub_item + "',"
                        if sub_item:
                            sql = sql + "'" + token + "')"   
                            print sql                                                     
                            insert(sql)                               
                   
                    incomingMsisdn[14] = -1
                    list_airlines = ""                        
                                             
            else:
                answer = "Bang Joni tidak menemukan penerbangan. Sebut aja tanggal atau rute lainnya."                    
                sendMessageT2(msisdn, answer, 0)
                incomingMsisdn[14] = -1   
                incomingMsisdn[15] = 2  


        elif answer[:4] == "fl02":
            bookingMsisdn = json.loads(lineNlp.redisconn.get("book/%s" % (msisdn)))		
            sql = "select * from searching_airlines where msisdn = '%s' and id = %s" % (msisdn, bookingMsisdn['flight_id'])
            print sql
            sqlout = request(sql)
            departure_date = ""
            for row in sqlout:
                flight_id = row[3]
                token = row[8]
                departure_date = row[1]
                flight_number = row[4]
                airlines_name = row[5]
                departure_time = row[6]
            if departure_date != "":
                web_request = "http://128.199.139.105/flight/form_wh.php?date=%s&ret_date=x&flight_id=%s&ret_flight_id=x&token=%s" % (departure_date, flight_id, token)
                bookingMsisdn['flight_id'] = flight_id
                bookingMsisdn['token'] = token  
                incomingMsisdn[18] = flight_number    
                incomingMsisdn[19] = airlines_name 
                incomingMsisdn[20] = departure_time                                                                                         
                print web_request
                respAPI = fetchHTML(web_request)
                print respAPI
                if respAPI.find("<ADULT>") >= 0:
                    if respAPI.find("passportno") == -1:
                        if incomingMsisdn[9] > 0 and incomingMsisdn[10] == 0 and incomingMsisdn[11] == 0:
                            answer = "Format penumpang untuk %s dewasa" % (incomingMsisdn[9])
                            answer = answer + ", dg format: (Tn/Ny/Nona)/nama lengkap/tgl lahir/"                                                         
                        elif incomingMsisdn[9] > 0 and incomingMsisdn[10] > 0 and incomingMsisdn[11] == 0:
                            answer = "Format penumpang untuk %s dewasa %s anak" % (incomingMsisdn[9], incomingMsisdn[10])
                            answer = answer + ", dg format: (d=dewasa/a=anak)/(Tn/Ny/Nona)/nama lengkap/tgl lahir/"
                        elif incomingMsisdn[9] > 0 and incomingMsisdn[10] > 0 and incomingMsisdn[11] > 0:    
                            answer = "Format penumpang untuk %s dewasa %s anak %s bayi" % (incomingMsisdn[9], incomingMsisdn[10], incomingMsisdn[11])
                            answer = answer + ", dg format: (d=dewasa/a=anak/b=bayi)/(Tn/Ny/Nona)/nama lengkap/tgl lahir/"
                    else:
                        incomingMsisdn[16] = 1
                        if incomingMsisdn[9] > 0 and incomingMsisdn[10] == 0 and incomingMsisdn[11] == 0:
                            answer = "Format penumpang untuk %s dewasa" % (incomingMsisdn[9])
                            answer = answer + ", dg format: (Tn/Ny/Nona)/nama lengkap/tgl lahir/no paspor/negara penerbit paspor/tgl terbit paspor/tgl expired paspor/"                         
                        elif incomingMsisdn[9] > 0 and incomingMsisdn[10] > 0 and incomingMsisdn[11] == 0:
                            answer = "Format penumpang untuk %s dewasa %s anak" % (incomingMsisdn[9], incomingMsisdn[10])
                            answer = answer + ", dg format: (d=dewasa/a=anak)/(Tn/Ny/Nona)/nama lengkap/tgl lahir/no paspor/negara penerbit paspor/tgl terbit paspor/tgl expired paspor/"
                        elif incomingMsisdn[9] > 0 and incomingMsisdn[10] > 0 and incomingMsisdn[11] > 0:    
                            answer = "Format penumpang untuk %s dewasa %s anak %s bayi" % (incomingMsisdn[9], incomingMsisdn[10], incomingMsisdn[11])
                            answer = answer + ", dg format: (d=dewasa/a=anak/b=bayi)/(Tn/Ny/Nona)/nama lengkap/tgl lahir/no paspor/negara penerbit paspor/tgl terbit paspor/tgl expired paspor/"                                                   
                        
                    if respAPI.find("dcheckinbaggagea") != -1:
                        answer = answer + "(0,15,20,25,30,35,40)kg;"
                        incomingMsisdn[17] = 1
                            
                    if respAPI.find("passportno") == -1 and respAPI.find("dcheckinbaggagea") == -1:
                        if incomingMsisdn[9] > 0 and incomingMsisdn[10] == 0 and incomingMsisdn[11] == 0:
                            answer = answer + "\n" + "Contoh: Tn/kenzie abinaya/5mei1980/"  
                        elif incomingMsisdn[9] > 0 and incomingMsisdn[10] > 0 and incomingMsisdn[11] == 0:
                            answer = answer + "\n" + "Contoh: d/Tn/kenzie abinaya/5mei1980/" + "\n" + "a/Nona/keke abinaya/5mei2008/"  
                        elif incomingMsisdn[9] > 0 and incomingMsisdn[10] > 0 and incomingMsisdn[11] > 0:    
                            answer = answer + "\n" + "Contoh: d/Tn/kenzie abinaya/5mei1980/" + "\n" + "a/Nona/keke abinaya/5mei2008/" + "\n" + "b/Nona/kia abinaya/5mei2014/"
                                   
                    if respAPI.find("passportno") == -1 and respAPI.find("dcheckinbaggagea") != -1:
                        if incomingMsisdn[9] > 0 and incomingMsisdn[10] == 0 and incomingMsisdn[11] == 0:
                            answer = answer + "\n" + "Contoh: Tn/kenzie abinaya/5mei1980/15/"  
                        elif incomingMsisdn[9] > 0 and incomingMsisdn[10] > 0 and incomingMsisdn[11] == 0:
                            answer = answer + "\n" + "Contoh: d/Tn/kenzie abinaya/5mei1980/15/" + "\n" + "a/Nona/keke abinaya/5mei2008/0/"  
                        elif incomingMsisdn[9] > 0 and incomingMsisdn[10] > 0 and incomingMsisdn[11] > 0:    
                            answer = answer + "\n" + "Contoh: d/Tn/kenzie abinaya/5mei1980/15/" + "\n" + "a/Nona/keke abinaya/5mei2008/0/" + "\n" + "b/Nona/kia abinaya/5mei2014/0/"                                    
                         
                    incomingMsisdn[15] = 3
                else:
                    answer = "Maaf, terjadi kesalahan, mohon coba lagi"
                    incomingMsisdn = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""]
                sendMessageT2(msisdn, answer, 0)
                lineNlp.redisconn.set("book/%s" % (msisdn), json.dumps(bookingMsisdn))				
                    
         
        elif answer[:4] == "fl06":
            bookingMsisdn = json.loads(lineNlp.redisconn.get("book/%s" % (msisdn)))		
            ask = "fl04aa"
            print "AAAAAAAAAAAAAAAAAAAA"
            answer = lineNlp.doNlp(ask, msisdn, first_name)
            print "BBBBBBBBBBBBBBBBBBBB"
            print bookingMsisdn        
            print incomingMsisdn			
            log_book(logDtm, msisdn, first_name, "FLIGHT", incomingMsisdn[2] + "-" + incomingMsisdn[3] + "-" + incomingMsisdn[4] + "-" + incomingMsisdn[19] + "-" + incomingMsisdn[20] + "-" + incomingMsisdn[16])			
            incomingMsisdn[14] = 1                    
            s = ""                    
            logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')   
            for key in bookingMsisdn:
                s = s + key + "=" + bookingMsisdn[key] + "&"                                                              
            s = s + "paymentmethod=" + urllib.quote_plus(incomingMsisdn[16])               
            s = "http://128.199.139.105/flight/order_wh1.php?" + s    
            print s
            respAPI = fetchHTML(s)   
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
                    randomDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y%m%d%H%M%S')
                    pdf2jpg.write("%s_%s.jpg" % (outfile.split('.')[0], randomDtm))  

                    #goHtml2Png(respAPI, msisdn)
                    print "Done convert html to pdf to png"                                                
                    #photo = open('%s.jpg' % (outfile.split('.')[0]), 'rb')
                    sendPhotoT2(msisdn, '%s_%s.jpg' % (outfile.split('.')[0], randomDtm))
                         
                    sqlstart = respAPI.find("<TOKEN>")
                    sqlstop = respAPI.find("</TOKEN>")
                    token = respAPI[sqlstart+7:sqlstop]   
                    sqlstart = respAPI.find("<ORDERID>")
                    sqlstop = respAPI.find("</ORDERID>")
                    orderid = respAPI[sqlstart+9:sqlstop]                                                    
                    sqlstart = respAPI.find("<URL_PAYMENT>")
                    sqlstop = respAPI.find("</URL_PAYMENT>")
                    url_payment = respAPI[sqlstart+13:sqlstop]   

                    sql = "insert into booking_tickets values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (logDtm, msisdn, incomingMsisdn[21], incomingMsisdn[22], incomingMsisdn[2], incomingMsisdn[20], incomingMsisdn[18], incomingMsisdn[19], orderid, token, s)                                      
                    insert(sql)                                                
                    time.sleep(3)

                    if incomingMsisdn[16] == "ATM Transfer":
					    #s = "http://128.199.139.105/bayar_wh.php?s=https://api.tiket.com/checkout/checkout_payment/35&token=" + incomingMsisdn[13]                        
                        s = "http://128.199.139.105/flight/bayar_wh.php?s=%s&token=%s" % (url_payment, incomingMsisdn[13])
                        print s                         
                        respAPI = fetchHTML(s)  
                        if respAPI.find("Ringkasan Pembayaran") >= 0:    
                            #goHtml2Png(respAPI, msisdn + "_bayar")
                            #print "Done convert html to png"    
                            incomingMsisdn = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""]  
                            bookingMsisdn = {}                            
                            #sendImg("/tmp/%s_bayar.jpg" %(msisdn), msisdn)
                            print "Sukses ATM:"
                        else: 
                            #print "Bayar error:", respAPI
                            answer = "Maaf, order pembayaran via ATM tdk bisa, ulangi lagi ya..."
                            print answer
                            err_msg = respAPI[respAPI.find("error_msgs")+10:respAPI.find("status")]   
                            err_msg = err_msg.translate(None, ",'!.?$%:\"")
                            try:
                                sql = "insert into booking_error values('%s','%s','%s','%s','%s')" % (logDtm, msisdn, incomingMsisdn[13], s, err_msg)                                      
                                insert(sql)  
                            except:
                                print "sql error at order gopegi"  
                            answer = answer + ": " + err_msg
                            sendMessageT2(msisdn, answer, 0)
                            incomingMsisdn = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""]  
                            bookingMsisdn = {}
                            lineNlp.redisconn.set("book/%s" % (msisdn), json.dumps(bookingMsisdn))							
                    elif incomingMsisdn[16] == "Credit Card" or incomingMsisdn[16] == "CIMB Clicks" or incomingMsisdn[16] == "BCA KlikPay":
                        url = "https://tiket.com/payment/checkout_payment?currency=IDR&token=%s&checkouttoken=%s&payment_type=%s" % (token, token, url_payment.split("=")[1])
                        print "Tiketdotcom_payment:", url
                        #sendMessageT2(msisdn, "Bang Joni berhasil booking tiketmu.\nUntuk melakukan pembayaran via %s <a href=\"%s\">click disini</a>.\nBang Joni segera kirim tiket setelah pembayaran." % (incomingMsisdn[16], url), 0)
                        sendLinkMessageT2(msisdn, 'berhasil booking, segera lakukan pembayaran via %s.\nBang Joni segera kirim tiket setelah pembayaran diterima' % (incomingMsisdn[16]), incomingMsisdn[16], 'Bayar Sekarang', url, 'http://128.199.88.72/line_images/logobangjoni2.jpg')						
                    else:
                        url = "https://api.tiket.com/payment/checkout_payment?currency=IDR&token=%s&checkouttoken=%s&payment_type=%s" % (token, token, url_payment.split("=")[1])
                        print "Tiketdotcom_payment:", url
                        #sendMessageT2(msisdn, "Bang Joni berhasil booking tiketmu.\nUntuk melakukan pembayaran via %s <a href=\"%s\">click disini</a>.\nBang Joni segera kirim tiket setelah pembayaran." % (incomingMsisdn[16], url), 0)
                        sendLinkMessageT2(msisdn, ' berhasil booking, segera lakukan pembayaran via %s.\nBang Joni segera kirim tiket setelah pembayaran diterima' % (incomingMsisdn[16]), incomingMsisdn[16], 'Bayar Sekarang', url, 'http://128.199.88.72/line_images/logobangjoni2.jpg')						

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
                    sql = "insert into booking_error values('%s','%s','%s','%s','%s')" % (logDtm, msisdn, incomingMsisdn[13], s, err_msg)                                      
                    print sql
                    insert(sql)  
                except:
                    print "sql error at order gopegi"
                answer = answer + ": " + err_msg
                sendMessageT2(msisdn, answer, 0)
                incomingMsisdn = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""]  
                bookingMsisdn = {}
                lineNlp.redisconn.set("book/%s" % (msisdn), json.dumps(bookingMsisdn))				
        #elif answer.find("Maaf") >= 0:
            #pass

####################LOG MESSAGES####################
        #sql = "insert into asking_request values('" + logDtm + "','" + msisdn + "','" + first_name + "','" + ask + "')"
        #print sql
        #sql = "insert into asking_response values('" + logDtm + "','" + msisdn + "','" + first_name + "','" + answer + "')"
        #print sql
#################################################

####################UPDATE REDIS INCOMING MSISDN####

####################ECOMMERCE MODULE START####################
        if ask[:5] == "[LOC]" and incomingMsisdn[11] == "eco00":
            incomingMsisdn[2] = ask[5:].split(';')[0]
            incomingMsisdn[3] = ask[5:].split(';')[1]
            ecommanswer = lineNlp.doNlp("locationsaved", msisdn, first_name)
            do_ecommerce_event(msisdn,ask,first_name,ecommanswer,incomingMsisdn)
            print "Ecommerce sharing location"
        print "++++++++++++++++++", incomingMsisdn
        lineNlp.redisconn.set("inc/%s" % (msisdn), json.dumps(incomingMsisdn))










@app.task
def uber_request_ride_surge(surge_confirmation_id):
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
        sql = "select * from booking_uber where status = '%s'" % (surge_confirmation_id)
        print sql
        sqlout = request(sql)
        access_token = ""
        msisdn_uber = ""
        first_name = ""
        for row in sqlout:
            msisdn_uber = row[0]
            access_token = row[5]
            first_name = row[1]
        incomingMsisdn = json.loads(lineNlp.redisconn.get("inc/%s" % (msisdn_uber)))
        if access_token != "" and incomingMsisdn[2] != -1 and incomingMsisdn[3] != -1:
            print "http://128.199.139.105/uber/request_ride_surge.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&surge_id=%s&product=%s" % (incomingMsisdn[2], incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[5], access_token, surge_confirmation_id, incomingMsisdn[6])
            respAPI = fetchHTML("http://128.199.139.105/uber/request_ride_surge.php?slatitude=%s&slongitude=%s&elatitude=%s&elongitude=%s&access_token=%s&surge_id=%s&product=%s" % (incomingMsisdn[2], incomingMsisdn[3], incomingMsisdn[4], incomingMsisdn[5], access_token, surge_confirmation_id, incomingMsisdn[6]))   
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
                sendMessageT2(msisdn_uber, "Ok, Bang Joni order Uber dengan tarif peak...", 0)
                incomingMsisdn[6] = request_id
                incomingMsisdn[7] = access_token
                #insert("delete from booking_uber where msisdn = '%s'" % (msisdn))
                sql = "insert into booking_uber values('" + msisdn_uber + "','" + first_name + "','" + request_id + "','" + status + "','" + logDtm +  "','" + access_token + "','line')"
                print sql
                insert(sql)
                incomingMsisdn[11] = ""
            else:
                sendMessageT2(msisdn_uber, "Bang Joni, nggak dapat response dari Uber, coba lagi ya...", 0)
        lineNlp.redisconn.set("inc/%s" % (msisdn_uber), json.dumps(incomingMsisdn))


@app.task
def uber_send_notification(event_id, event_time, event_type, meta_user_id, meta_resource_id, meta_resource_type, meta_status, resource_href):
        sql = "select * from booking_uber where request_id = '%s'" % (meta_resource_id)
        print sql
        sqlout = request(sql)
        msisdn_uber = ""
        for row in sqlout:
            msisdn_uber = row[0]
            first_name = row[1]
            access_token = row[5]
        if msisdn_uber != "":
            incomingMsisdn = json.loads(lineNlp.redisconn.get("inc/%s" % (msisdn_uber)))
            sql = "update booking_uber set status = '%s' where msisdn = '%s' and request_id = '%s'" % (meta_status, msisdn_uber, meta_resource_id)
            print sql
            insert(sql)
            if meta_status == "accepted":
                print "http://128.199.139.105/uber/get_notified.php?status=accepted&access_token=%s&resourcehref=%s" % (access_token, urllib.quote_plus(resource_href))
                respAPI = fetchHTML("http://128.199.139.105/uber/get_notified.php?status=accepted&access_token=%s&resourcehref=%s" % (access_token, urllib.quote_plus(resource_href)))   
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
                    answer = "Bang Joni sudah mendapatkan Uber buatmu, estimasi kedatangan " + eta + " menit, berikut data driver-nya:"
                    #sendMessageT2(msisdn_uber, answer, 0)
                    f = open('/usr/share/nginx/html/line_images/' + driver_picture.split('/')[-1],'wb')
                    f.write(urllib.urlopen(driver_picture).read())
                    f.close()
                    answer = "Driver: " + driver_name + "\nHP: " + driver_phone + "\nRating: " + driver_rating + "\nKendaraan: " + vehicle_make + " " + vehicle_model + "\nNopol: " + license_plate
                    #sendPhotoT2(msisdn_uber, '/tmp/' + driver_picture.split('/')[-1], answer)
                    sendPhotoCaptionT2(msisdn_uber, 'http://128.199.88.72/line_images/%s' % (driver_picture.split('/')[-1]), 'http://128.199.88.72/line_images/%s' % (driver_picture.split('/')[-1]), answer)
                    logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')	
                    displayname = get_line_username(msisdn_uber)					
                    log_book(logDtm, msisdn_uber, displayname, "UBER", driver_name + "-" + driver_phone + "-" + license_plate)					
					
                    #f = open('/tmp/' + vehicle_picture.split('/')[-1],'wb')
                    #f.write(urllib.urlopen(vehicle_picture).read())
                    #f.close()
                    #answer = vehicle_model + ", Nopol " + license_plate
                    #sendPhotoT2(msisdn_uber, '/tmp/' + vehicle_picture.split('/')[-1], answer)
                    
                    
            if meta_status == "ready":
                print "http://128.199.139.105/uber/receipt_ride.php?access_token=%s&request_id=%s" % (access_token, meta_resource_id)
                respAPI = fetchHTML("http://128.199.139.105/uber/receipt_ride.php?access_token=%s&request_id=%s" % (access_token, meta_resource_id))   
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
                    sendMessageT2(msisdn_uber, answer, 0)
                else:
                    sendMessageT2(msisdn_uber, "Info charge, Bang Joni nggak dapat dari Uber", 0)
                    logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')	
                    displayname = get_line_username(msisdn_uber)					
                    log_paid(logDtm, msisdn_uber, displayname, "UBER", "")						

            if meta_status == "arriving":
                answer = "Uber-mu sudah mau sampe, siap-siap..."
                sendMessageT2(msisdn_uber, answer, 0)

            if meta_status == "in_progress":
                answer = "Safe trip ya, pangggil bang Joni lagi klo butuh uber"
                sendMessageT2(msisdn_uber, answer, 0)
                answer = lineNlp.doNlp("exittorandom", msisdn_uber, first_name)
                try:
                    incomingMsisdn = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,logDtm,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,"2016",""]  
                except:
                    print "Error cancel order"

            if meta_status == "no_drivers_available":  
                answer = "Bang Joni nggak nemu driver, kemungkinan lagi penuh.\nCoba lagi ntar ya.."
                sendMessageT2(msisdn_uber, answer, 0)
                answer = lineNlp.doNlp("exittorandom", msisdn_uber, first_name)

            if meta_status == "driver_canceled": 
                answer = "Driver-nya batalin pesenanmu.\nCoba lagi ntar ya.."
                sendMessageT2(msisdn_uber, answer, 0)
                answer = lineNlp.doNlp("exittorandom", msisdn_uber, first_name)
				
            if meta_status == "completed": 
                answer = "Bang Joni dapat pesen dari Uber: Terima Kasih telah memilih Uber dan sampai ketemu di perjalanan yg akan datang"
                sendMessageT2(msisdn_uber, answer, 0)
                answer = lineNlp.doNlp("exittorandom", msisdn_uber, first_name)		
        lineNlp.redisconn.set("inc/%s" % (msisdn_uber), json.dumps(incomingMsisdn))


@app.task
def uber_authorization(msisdn, code):
        print "uber_authorization >>>>>", msisdn, code
        sql = "select * from token_uber where state = '%s'" % (msisdn)
        print sql
        sqlout = request(sql)
        msisdn_uber = ""
        platform = ""
        email = ""
        for row in sqlout:
            msisdn_uber = row[0]
            platform = row[5]

    
        if msisdn_uber != "":
            incomingMsisdn = json.loads(lineNlp.redisconn.get("inc/%s" % (msisdn_uber)))
            #result_redirect = "https://www.bangjoni.com:8443/uber_token?state=%s&code=%s" % (msisdn, code)
            result_redirect = "https://www.bangjoni.com/uber_token?state=%s&code=%s" % (msisdn, code)			
            print ">>>", result_redirect
            try:
                #session = incomingMsisdn[1].get_session(result_redirect)
                xx = pickle.loads(incomingMsisdn[1])
                session = xx.get_session(result_redirect)                				

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
            insert(sql)  
            sql = "update token_uber set access_token='%s', refresh_token='%s', expires_in_sec='%s', email='%s' where email='%s'" % (credential.access_token, credential.refresh_token, credential.expires_in_seconds, email, email)
            print sql
            insert(sql)  			
            sendMessageT2(msisdn_uber, "Account ubermu sudah terhubung dengan BangJoni\nSekarang share lokasimu dengan cara click tombol PIN dan tap Location", 0)
        #return "Y" 


@app.task		
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
        sqlout = request(sql)
        msisdn = ""
        for row in sqlout:
            msisdn = row[1]
		
        if msisdn != "" and (status == "SUCCESS" or status == "FAILED" or status == "PENDING PAYMENT"):
            logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')	
            displayname = get_line_username(msisdn)					
            if cat == "pulsa_hp": 
                reply = "Sip, pembelian pulsa hp nomor %s sukses, cek di hpmu apakah pulsa sudah masuk" % (msisdn_pln)        	
                log_paid(logDtm, msisdn, displayname, "PULSA", msisdn_pln + "-" + trxid + "-" + status)				
            if cat == "token": 
                reply = "Sip, pembelian token listrik nomor meter %s sukses, nomor tokenmu %s dengan jumlah KWH %s" % (msisdn_pln, token, jml_kwh)  		
                log_paid(logDtm, msisdn, displayname, "PLN", msisdn_pln + "-" + trxid + "-" + status + "-" + token)					
            if status == "FAILED":
                reply = "Tunggu sebentar ya, transaksi masih pending, tunggu notifikasi sms ya untuk pulsa masuk"		
                log_paid(logDtm, msisdn, displayname, "PULSA/PLN", msisdn_pln + "-" + trxid + "-" + status)
            if status == "PENDING PAYMENT":
                reply = "Segera lakukan pembayaran %s di %s dengan kode pembayaran %s agar transaksimu tidak dibatalkan" % (cat, payment_channel, kode_bayar)			
                log_paid(logDtm, msisdn, displayname, "PULSA/PLN", msisdn_pln + "-" + trxid + "-" + status)				
            sendMessageT2(msisdn, reply, 0)
            sql = "update jatis_billers set trxid='%s', payment_channel='%s', status='%s' where lineid='%s' and msisdn_pln = '%s' and status = '' and substr(dtm,1,10) = '%s'" % (trxid, payment_channel, trxstatus, msisdn, msisdn_pln, trxtime[:10])
            print sql
            insert(sql) 			

@app.task
def docloudmailin(content):
        to_email = content['envelope']['to']
        from_email = content['envelope']['from']
        subject_email = content['headers']['Subject']
        date_email = content['headers']['Date']
        body_email = content['plain']
        content_type = content['headers']['Content-Type']
        body_email_html = content['html']

        try:
            attach_email = content['attachments'][0]['file_name']
            content_email = content['attachments'][0]['content']
        except:
            attach_email = ""
            content_email = ""

        if attach_email != "":
            f = open('/tmp/%s' % (attach_email), 'w')
            data = base64.decodestring(content_email)
            f.write(data)
            f.close()

        print to_email, from_email, subject_email, date_email, content_type, body_email, attach_email, content_email
        print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        print body_email_html
		
        body_email_html = body_email_html.replace("<b>","<strong>")
        body_email_html = body_email_html.replace("</b>","</strong>")
		
        if subject_email.find("Reminder Pembayaran Reservasi") >= 0:
            kodeBooking_exist = body_email_html.find("Kode Booking                : ")
            if kodeBooking_exist != -1:
                #a = body_email[body_email.find('Kode Booking'):]
                #kodebooking = (a[:a.find('\n')].split(':')[1]).strip()
                #a = body_email[body_email.find('Kode Pembayaran'):]
                #kodepembayaran = (a[:a.find('\n')].split(':')[1]).strip()
                #a = body_email[body_email.find('Batas Pembayaran'):]
                #bataspembayaran = (a[:a.find('\n')].split(':')[1]).strip()
                #a = body_email[body_email.find('Jumlah Yang Harus Dibayar'):]
                #jumlahbayar = (a[:a.find('\n')].split(':')[1]).strip()				               
			
                str_temp = body_email_html[kodeBooking_exist+30:]
                kodebooking = str_temp[0:str_temp.find("<br")].replace(" ","")
                str_temp = str_temp[str_temp.find("Kode Pembayaran             : ")+30:]
                kodepembayaran = str_temp[0:str_temp.find("<br")]
                str_temp = str_temp[str_temp.find("Batas Pembayaran            : ")+30:]
                bataspembayaran = str_temp[0:str_temp.find("<br")]
                str_temp = str_temp[str_temp.find("Jumlah Yang Harus Dibayar   : ")+30:]
                jumlahbayar = str_temp[0:str_temp.find("<br")]
                			
                print "--->", kodebooking, kodepembayaran, bataspembayaran, jumlahbayar
                filename = "TIKETTUX." + kodebooking + ".html"                          
                resp = "Bang Joni sekedar mengingatkan, kamu belum melakukan pembayaran reservasi xtrans.\nBatas pembayaran sampai %s, lebih dari itu Bang Joni batalin ya." % (bataspembayaran)
                print resp
                onEmailReceived(filename, resp)

        if subject_email.find("Permohonan Pembayaran Order ID") >= 0:
            va_number_exist = body_email_html.find("VA number     : <strong>")
            #PERMATA
            if va_number_exist != -1:		
                #a = body_email[body_email.find('VA number '):]
                #va_number = (a[:a.find('\n')].split(':')[1]).strip().replace("*","")
                #a = body_email[body_email.find('Jumlah'):]
                #jumlah = (a[:a.find('\n')].split(':')[1]).strip().replace("*","")
                #a = body_email[body_email.find('Waktu Booking'):]
                #waktu_booking = (a[:a.find('\n')].split(': ')[1]).strip().replace("*","")
                #a = body_email[body_email.find('Waktu Expired'):]
                #waktu_expired = (a[:a.find('\n')].split(': ')[1]).strip().replace("*","")		

                str_temp = body_email_html[va_number_exist+24:]
                va_number = str_temp[0:str_temp.find("</strong>")].replace(" ","")
                str_temp = str_temp[str_temp.find("Jumlah        : <strong>")+24:]
                jumlah = str_temp[0:str_temp.find("</strong>")]
                str_temp = str_temp[str_temp.find("Waktu Booking : <strong>")+24:]
                waktu_booking = str_temp[0:str_temp.find("</strong>")]
                str_temp = str_temp[str_temp.find("Waktu Expired : <strong>")+24:]
                waktu_expired = str_temp[0:str_temp.find("</strong>")]

				
                print "PERMATA: va number: ", va_number, jumlah, waktu_booking, waktu_expired
                filename = re.findall(r'\d+', subject_email)[0] + ".html"                          
                resp = "Pesanan tiket sudah Bang Joni booking.\nSilakan lakukan transaksi pembayaran tiket pesawat sejumlah %s ke: \nBank: Permata kode 013\nNo Rek: %s\nLakukan pembayaran secepatnya sebelum %s supaya tiket kamu tidak dibatalkan.\nBang Joni akan kirim tiket jika pembayaran telah diterima" % (jumlah, va_number, waktu_expired)
                print resp
                onEmailReceived(filename, resp)
			
            else:
                #ARTA JASA
                va_number_exist = body_email_html.find("Kode Bank")
                if va_number_exist != -1:	
                    str_temp = body_email_html[va_number_exist:]
                    str_temp = str_temp[str_temp.find("<strong>")+8:]
                    va_number = str_temp[0:str_temp.find("</strong>")]

                    str_temp = content[content.find("Jumlah"):]
                    str_temp = str_temp[str_temp.find("<strong>")+8:]
                    jumlah = str_temp[0:str_temp.find("</strong>")]

                    str_temp = content[content.find("Waktu Booking"):]
                    str_temp = str_temp[str_temp.find("<strong>")+8:]
                    waktu_booking = str_temp[0:str_temp.find("</strong>")]

                    str_temp = content[content.find("Waktu Expired"):]
                    str_temp = str_temp[str_temp.find("<strong>")+8:]
                    waktu_expired = str_temp[0:str_temp.find("</strong>")]

                    str_temp = content[content.find("Nomor Rekening"):]
                    str_temp = str_temp[str_temp.find("<strong>")+8:]
                    nomor_rekening = str_temp[0:str_temp.find("</strong>")]

                    print "ARTAJASA: va number: ", va_number, jumlah, waktu_booking, waktu_expired, nomor_rekening
                    filename = re.findall(r'\d+', subject_email)[0] + ".html"                          
                    resp = "Pesanan tiket sudah Bang Joni booking.\nSilakan lakukan transaksi pembayaran tiket pesawat sejumlah %s ke: \nBank Artajasa kode institusi %s\nNo Rek: %s\nLakukan pembayaran secepatnya sebelum %s supaya tiket kamu tidak dibatalkan.\nBang Joni akan kirim tiket jika pembayaran telah diterima" % (jumlah, va_number, nomor_rekening, waktu_expired)
                    print resp
                    onEmailReceived(filename, resp)

        # ---------- DWP MODULE START ----------
        if subject_email.find("eVoucher for") >= 0 and from_email.find("mandrillapp.com") >= 0:
            #body_email_html.find("Silahkan mencetak e-voucher yang kami sediakan pada")
            # print body_email.find("<https://neo.loket.com/evoucher")
            if body_email_html.find("Silahkan mencetak e-voucher yang kami sediakan pada <a href=") > 1:
                evoucherLink = body_email_html[body_email_html.find("Silahkan mencetak e-voucher yang kami sediakan pada <a href=") + 61: body_email_html.find(">tautan berikut</a>") - 48]
                bookingId = subject_email[subject_email.find("[#")+2:subject_email.find("]")]
                msisdn = dwp.getUidFromBookingCode(bookingId)
                sendLinkMessageT2(msisdn, "e-Ticket DWP", "Tukar e-ticket dgn tiket asli sblm masuk venue", "Lihat e-ticket", evoucherLink, "https://pbs.twimg.com/profile_images/793389395080384513/OXfXpsjj.jpg")
                sendMessageT2(msisdn, "Jangan lupa tuker E-Ticket DWP kamu dengan tiket asli DWP di,\n\nMall Gandaria City\nTanggal 5 - 8 Desember 2016\nDari jam 10:00 - 21:00 WIB\n\nPenukaran tiket harus dilakukan oleh pembeli tiket disertai dengan menunjukkan KTP asli dan tidak dapat diwakilkan.\n\nSee you at DWP 2016 guys!", 0)
            elif body_email.find("<https://neo.loket.com/evoucher") > 1:
                evoucherLink = body_email[body_email.find("<https://neo.loket.com/evoucher")+1 : body_email.find(">")]
                bookingId = subject_email[subject_email.find("[#") + 2:subject_email.find("]")]
                msisdn = dwp.getUidFromBookingCode(bookingId)
                sendLinkMessageT2(msisdn, "e-Ticket DWP", "Tukar e-ticket dgn tiket asli sblm masuk venue", "Lihat e-ticket", evoucherLink, "https://pbs.twimg.com/profile_images/793389395080384513/OXfXpsjj.jpg")
                sendMessageT2(msisdn, "Jangan lupa tuker E-Ticket DWP kamu dengan tiket asli DWP di,\n\nMall Gandaria City Mall, Piazza Hall\nLantai G (Main St. Area)\nJl. Sultan Iskandar Muda, Jakarta Selatan,\nDKI Jakarta 12240\n\nSenin – Kamis, 5 - 8 Desember 2016\n10:00 - 21:00 WIB\n\nUntuk info lebih lanjut kamu bisa hubungin, ticketing@djakartawarehouse.com", 0)
                linebot.send_images(msisdn, "http://bangjoni.com/dwp_images/dwp_tc/SYARAT PENUKARAN_1011.jpeg", "http://bangjoni.com/dwp_images/dwp_tc/SYARAT PENUKARAN_240.jpeg")
                logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
                log_paid(logDtm, msisdn, get_line_username(msisdn), "DWP", "")
        # ---------- DWP MODULE END ----------

        if attach_email != "" and os.path.exists('/tmp/%s' % (attach_email)) and attach_email.endswith('.pdf'):
            if subject_email.find("eTicket") >= 0 and subject_email.find("Tiket.com") >= 0:
                filename = re.findall(r'\d+', subject_email)[0] + ":" + attach_email  
                print "eTicket:", filename                        
                onEmailReceived(filename, "pdf")           
                

				
            if subject_email.find("Tiket Xtrans") >= 0 or subject_email.find("Tiket %s" %(attach_email.split(".")[0])) >= 0:				
                filename = "999:" + attach_email  
                print "eTicket:", attach_email                        
                onEmailReceived(filename, "pdf")			
				
                      
@app.task
def doagentresp(content):
        print content
        print content['rive']
        reply = ""
        try:
            #reply = content['msg'].split("-")[1].strip()
            reply = content['msg'].split("-")
            if len(reply) > 1:
                reply = reply[1].strip()
                if content['msg'][0] == "+" and reply != "":
                    if "<first_name>" in reply:
                        displayname = get_line_username(content['msisdn'])
                        reply = reply.replace("<first_name>", displayname)		
                    sendMessageT2(content['msisdn'], reply, 0)
                    lineNlp.updateNlp(content['msg'])			
            elif content['msg'][0] != "+" and content['msg'][0] != "":
                sendMessageT2(content['msisdn'], content['msg'], 0)		
            else:				
                print "REPLY FROM AGENT ERROR" 
        except:
            print "REPLY FROM AGENT ERROR"  

		
@app.task
def doloadtest():				
        print "testloads"
        #onMessage(str("load/%s" % (random.randrange(1, 10000))), "testloads", "testload")
        onMessage(str("load/%s" % (random.randrange(1, 10000))), "galon", "testload")		

		
@app.task
def doworker(req):
        content = json.dumps(req)
        content = json.loads(content)		
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
        stickerid = ""		
        contentType = 0
        opType = ""
		
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
                stickerid = content["result"][0]["content"]["contentMetadata"]["STKID"]		
                print "--->STICKER", sticker, stickerid  			
                sendMessageT2(msisdn, "Makasih sticker-nya..", 0)				
            if contentType == 2:
                print "--->IMAGE"
                sendMessageT2(msisdn, "Makasih sharing fotonya ya..", 0)
        except:
            opType = content["result"][0]["content"]["opType"]
            msisdn = str(content["result"][0]["content"]["params"][0])	
            print "-->", opType, msisdn			
			
        
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
        
        if contentType == 1 or contentType == 7: # request text location
            print "Incoming>>>", logDtm, first_name, msisdn, ask, longitude, latitude, username

            incomingClient = lineNlp.redisconn.get("status/%s" % (msisdn))            			
            if incomingClient is None:
                lineNlp.redisconn.set("status/%s" % (msisdn), 0)
                incomingClient = "0"

            #if incomingClient == "0":
                #lineNlp.redisconn.set("status/%s" % (msisdn), 1)
            if longitude != "":
                ask = "[LOC]" + str(latitude) + ";" + str(longitude)
                print ">>>>>>>", longitude, ask
            displayname = get_line_username(msisdn)
            #try:
            onMessage(str(msisdn), ask, displayname)
            #lineNlp.redisconn.set("status/%s" % (msisdn), 0)
            #    except Exception, e:
            #        print "ERROR HAPPEN!!!"
            #        print str(e)
                    #lineNlp.redisconn.set("status/%s" % (msisdn), 0)
                    #lineNlp.redisconn.delete("rs-users/%s" % (msisdn))
        elif opType == 4 or opType == 8: # request add friend and unblock
            displayname = get_line_username(msisdn)		
            reply = "Halo " + displayname + ", terima kasih telah add Bang Joni sebagai teman.\n\nBang Joni adalah teman virtual kamu yang bisa diandalkan kapan aja dan di mana aja.\nSekarang Bang Joni bisa bantu kamu pesen tiket pesawat, travel xtrans, uber, isi pulsa, isi token pln, infoin jalan tol dan cuaca, terjemahkan bahasa.\n\n"
            reply = reply + "Untuk memulai ketik aja \"Halo bang\"\n\nOh iya, pake penulisan yang benar ya, jangan terlalu banyak singkatan, biar Bang Joni nggak bingung."
            sendMessageT2(msisdn, reply, 0)     
            log_addfriends(logDtm, msisdn, displayname, "ADD FRIENDS")			

# ---------- DWP MODULE START ----------
@app.task
def updateDWPInvoice(bookingId, amountPay):
    print "update invoice "+bookingId
    # msisdn = dwp.getUidFromBookingCode(bookingId)
    msisdn = dwp.getUidFromAmountPay(amountPay)
    errorCode = dwp.updateInvoiceAsPaid(bookingId, Decimal(amountPay))
    lineusername = get_line_username(msisdn)
    if errorCode == 0:
        bookingId = dwp.getBookingCodeFromAmountPay(amountPay)
        # '{0:,}'.format(1000000)
        amountPay = '{0:,}'.format(Decimal(amountPay))
        reply = "Hai "+lineusername+", pembayaran tiket DWP kamu dengan kode booking "+bookingId+" sebanyak Rp "+amountPay+" udah Bang Joni terima ya."
        # reply = "Pembayaran DWP kamu dgn booking code "+bookingId+" sebanyak Rp. "+amountPay+" udah Bang Joni terima yaa, see you on stage guys ;)"
    else:
        reply = dwp_error_msg(errorCode,msisdn,lineusername)
    sendMessageT2(msisdn, reply, 0)
# ---------- DWP MODULE END ----------

# ---------- LOVIDOVI MODULE START ----------
@app.task
def handlePostbackLovidovi(itemId, userId, action, itemName, price):
    sendMessageT2(userId,"kamu memilih item : "+itemName, 0)
    ask = "input_order_bunga_"+itemName+"_"+itemId
    onMessage(str(userId), ask, get_line_username(userId))
    print "halo lovidovi"
# ---------- LOVIDOVI MODULE END ----------



@app.task
def depositNotification(trx_id):
    r = (datetime.now() + timedelta(hours=0)).strftime('%Y%m%d%H%M%S')
    signature = hashlib.md5('bangjoni' + r + 'bang567jon1').hexdigest()
    print signature

    payload = { 'command': 'validatetrx', 'username': 'bangjoni', 'time': r, 'trx_id': trx_id, 'signature': signature }

    headers = {'content-type': 'application/json'}
    resp = requests.post('https://cyrusku.cyruspad.com/pgw/pgwapi.asp', data=json.dumps(payload), headers=headers)
    content = resp.text
    print content
    content = json.loads(content)	
	
	response = content['Response']
    if response == "0":	
	    va_no = content['va_no']	
	    amount = content['amount']
	    mutasi = content['mutasi']     
	    snapshot_time = content['snapshot_time']	
	    bank_date = content['bank_date']
	    cust_id = content['cust_id']    

        if va_no[:6] == "865010":
            sql = "select msisdn from bjpay where va_no = '%s' limit 1" % (va_no)   		
        else:
            sql = "select msisdn from bjpay where amount = %s limit 1" % (amount)   		    
        
        print sql
        sqlout = request(sql)
        msisdn = ""
        for row in sqlout:
            msisdn = row[0]
			
        if msisdn != "":
            payload = lineNlp.redisconn.get("bjpay/%s" % (msisdn))
            balance = int(payload.split('|')[0])     
            va_no = payload.split('|')[1]
            deposit_hp = payload.split('|')[2] 							
            balance = balance + amount
            payload = balance + "|" + va_no + "|" + deposit_hp						
            lineNlp.redisconn.set("bjpay/bal/%s" % (msisdn), payload)	       		

			
			
			
#Second Initialization
print "Line bang joni bot personal assistant is online"

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

setup_logger('F_SRVC', '/home/bambangs/LOGBJ/F_SRVC.log')
setup_logger('F_BOOK', '/home/bambangs/LOGBJ/F_BOOK.log')
setup_logger('F_PAID', '/home/bambangs/LOGBJ/F_PAID.log')
setup_logger('F_NOREPLY', '/home/bambangs/LOGBJ/F_NOREPLY.log')
setup_logger('F_ADDFRIENDS', '/home/bambangs/LOGBJ/F_ADDFRIENDS.log')
F_SRVC = logging.getLogger('F_SRVC')
F_BOOK = logging.getLogger('F_BOOK')
F_PAID = logging.getLogger('F_PAID')
F_NOREPLY = logging.getLogger('F_NOREPLY')  
F_ADDFRIENDS = logging.getLogger('F_ADDFRIENDS')  

