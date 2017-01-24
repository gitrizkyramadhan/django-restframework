#python ./oauth2.py --user=bambang.sso@gmail.com --client_id=208964482452-u49no6r65fvtj4g7fk5klo670pra1uvp.apps.googleusercontent.com --client_secret=AvlmF_FfYZ_MdOU8weJR7D3I --refresh_token=1/tk3q5zUMAfNuBo0BjMXBDJ_DnLdLkMFqNgq5iKfy7FM
#Access Token: ya29.qAGP-cTpZkleekHXcvuWObEMRYcZwccoZnCS6k30GHeYgwJ0AGebRYwkh16OjOKWAKG6BKlCcJUZ_A
#Access Token Expiration Seconds: 3600
#Tiket.com Permohonan Pembayaran Order ID #24230871 menggunakan Transfer ATM (Instant Confirmation). 
#Lion Air KNO CGK eTicket - Tiket.com Order ID #24231528 and Item Number 17874509

import threading, imaplib2, os, sys, getpass
import pprint
import email
import inspect, shlex, time
import json
import urllib
from datetime import datetime, timedelta
import re


ServerTimeout = 29 # Mins

class idlerInit(object):
    def __init__(self, desc):
       self.desc = desc
       print "at _init_ idlerInit", self.desc


    def __call__(self, fn):
       fn.idlerdesc = self.desc
       print "at _call_ idlerInit", fn
       return fn


class Idler(object):

    stopWaitingEvent = threading.Event()
    
    knownAboutMail = [] # will be a list of IDs of messages in the inbox
    killNow = False # stops execution of thread to allow propper closing of conns.
    response = ""
    auth_string = ""
    imap = ""
    idleStatus = "" 
    
    GOOGLE_ACCOUNTS_BASE_URL = 'https://accounts.google.com'
    #client_id = '1066256155381-q4o76q0sptev7gpb2e8bt1hkc4fkuvj8.apps.googleusercontent.com'
    #client_secret = 'HdooSC1ZQjRMSor73LQk_nDj'
    #refresh_token = '1/0jUp31uPq2w3ACsTbN-SSxFrLBDxDBg2Cqh7d3jrQZU'
    client_id = '470373722824-e3olntu23ebb9aablf5misfj3j72lg2p.apps.googleusercontent.com'
    client_secret = 'pmJXXs0joZhu_zNUAYp_1kZc'
    refresh_token = '1/Gc8HVoR1c34_jcg8QaedIFBM1ctC-BfjnaPhRhvBtqU'
    
    def __init__(self):
        
        self.list_fn = {}
        members = inspect.getmembers(self, predicate = inspect.ismethod)
        for m in members:
            if hasattr(m[1], "idlerdesc"):
                print ">", m[0],m[1]
                self.list_fn[m[0]] = m[1]
        print self.list_fn        
        
        
        self.checkEmailThread = threading.Thread(target = self.doCheckNewEmail)
        self.checkEmailThread.daemon = True
        self.checkEmailThread.start()
                    
            
    def AccountsUrl(self, command):
        return '%s/%s' % (self.GOOGLE_ACCOUNTS_BASE_URL, command)
                
    def RefreshToken(self, client_id, client_secret, refresh_token):
        params = {}
        params['client_id'] = self.client_id
        params['client_secret'] = self.client_secret
        params['refresh_token'] = self.refresh_token
        params['grant_type'] = 'refresh_token'
        request_url = self.AccountsUrl('o/oauth2/token')
        response = urllib.urlopen(request_url, urllib.urlencode(params)).read()
        print response
        return json.loads(response)
         

    def doCheckNewEmail(self):
        timegap = 0
        t1 = datetime.now()
        print "T1: ", t1
        while True:
            logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            if timegap == 0 or timegap > 14400 or self.idleStatus == "idle_error":
                self.response = self.RefreshToken(self.client_id, self.client_secret,self.refresh_token)   
                self.auth_string = 'user=%s\1auth=Bearer %s\1\1' % ('bangjoniline@gmail.com',self.response['access_token'])                 
                self.imap = imaplib2.IMAP4_SSL("imap.gmail.com")            
                try:
                    self.imap.authenticate('XOAUTH2', lambda x: self.auth_string)
                    self.imap.SELECT("INBOX")

                except:
                    print 'ERROR: IMAP Issue. Exit...'
                    sys.exit(1) 

                print "New Token: ", self.response['access_token'], logDtm, timegap, self.idleStatus
                self.initCheck()
            
            self.waitForServer()
            t2 = datetime.now()
            delta = t2 - t1
            timegap = delta.total_seconds()
            print "T2: ", t2, timegap
            logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            if timegap > 14400 or self.idleStatus == "idle_error":
                t1 = t2
                try:
                    self.imap.CLOSE()
                    self.imap.LOGOUT()
                except:
                    print "CLOSE IMAP ERROR", logDtm, timegap, self.idleStatus
                    time.sleep(2)
                print "imap logout", logDtm, timegap, self.idleStatus

    def showNewMailMessages(self):
        typ, data = self.imap.SEARCH(None, '(OR OR OR OR FROM "bambang.sso@gmail.com" FROM "noreply@tiket.com" FROM "confirmation@portal.lionair.co.id" FROM "noreply@tiketux.com" FROM "info@tiket.com" UNSEEN)')
        #typ, data = self.imap.SEARCH(None, '(OR OR OR FROM "bambang.sso@gmail.com" FROM "info@tiket.com" FROM "confirmation@portal.lionair.co.id" FROM "noreply@tiketux.com" UNSEEN)')
                
        logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        print ">>Got new email....", logDtm
        for id in data[0].split():
            typ, msg_data = self.imap.FETCH(id, '(RFC822)')           
            text = msg_data[len(msg_data)-2][1]
                  
            msg = email.message_from_string(text)            

            temp = self.imap.store(id,'+FLAGS', '\\Seen')

            print "From:", msg['From']
            print "Subject:", msg['Subject']
            
            

            for part in msg.walk():
                if part.get_content_type() == 'text/html' and msg['Subject'].find("Reminder Pembayaran Reservasi") >= 0:
                    content = part.get_payload(decode=True)
                    
                    print ">>", content
                    kodeBooking_exist = content.find("Kode Booking                : ")
                    if kodeBooking_exist != -1:
                        str_temp = content[kodeBooking_exist+30:]
                        kodebooking = str_temp[0:str_temp.find("<br")].translate(None," ")
                        str_temp = str_temp[str_temp.find("Kode Pembayaran             : ")+30:]
                        kodepembayaran = str_temp[0:str_temp.find("<br")]
                        str_temp = str_temp[str_temp.find("Batas Pembayaran            : ")+30:]
                        bataspembayaran = str_temp[0:str_temp.find("<br")]
                        str_temp = str_temp[str_temp.find("Jumlah Yang Harus Dibayar   : ")+30:]
                        jumlahbayar = str_temp[0:str_temp.find("<br")]
                        print "--->", kodebooking, kodepembayaran, bataspembayaran, jumlahbayar
                        filename = "TIKETTUX." + kodebooking + ".html"                          
                        #resp = "Pesanan tiket sudah Bang Joni booking.\nBerikut detail pesanan kamu:\nKode booking: %s\nKode Pembayaran: %s\nJumlah Pembayaran: %s\nLakukan pembayaran secepatnya sebelum %s supaya tiket kamu tidak dibatalkan.\nBang Joni akan kirim tiket jika pembayaran telah diterima" % (kodebooking, kodepembayaran, jumlahbayar, bataspembayaran)
                        resp = "Bang Joni sekedar mengingatkan, kamu belum melakukan pembayaran reservasi xtrans.\nBatas pembayaran sampai %s, lebih dari itu Bang Joni batalin ya." % (bataspembayaran)
                        print resp
                        targetFn = self.list_fn["onEmailReceived"]
                        self.doExecCmd(lambda :targetFn(filename, resp))

                #PERMATA
                if part.get_content_type() == 'text/html' and msg['Subject'].find("Permohonan Pembayaran Order ID") >= 0:
                    content = part.get_payload(decode=True)

                    ##print ">>", content
                    va_number_exist = content.find("VA number     : <strong>")
                    if va_number_exist != -1:
                        str_temp = content[va_number_exist+24:]
                        va_number = str_temp[0:str_temp.find("</strong>")].translate(None," ")
                        str_temp = str_temp[str_temp.find("Jumlah        : <strong>")+24:]
                        jumlah = str_temp[0:str_temp.find("</strong>")]
                        str_temp = str_temp[str_temp.find("Waktu Booking : <strong>")+24:]
                        waktu_booking = str_temp[0:str_temp.find("</strong>")]
                        str_temp = str_temp[str_temp.find("Waktu Expired : <strong>")+24:]
                        waktu_expired = str_temp[0:str_temp.find("</strong>")]
                        print "PERMATA: va number: ", va_number, jumlah, waktu_booking, waktu_expired
                        filename = re.findall(r'\d+', msg['Subject'])[0] + ".html"                          
                        resp = "Pesanan tiket sudah Bang Joni booking.\nSilakan lakukan transaksi pembayaran tiket pesawat sejumlah %s ke: \nBank: Permata kode 013\nNo Rek: %s\nLakukan pembayaran secepatnya sebelum %s supaya tiket kamu tidak dibatalkan.\nBang Joni akan kirim tiket jika pembayaran telah diterima" % (jumlah, va_number, waktu_expired)
                        print resp
                        targetFn = self.list_fn["onEmailReceived"]
                        self.doExecCmd(lambda :targetFn(filename, resp))  
                    else:
                        #ARTA JASA
                        va_number_exist = content.find("Kode Bank")
                        if va_number_exist != -1:
                            str_temp = content[va_number_exist:]
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
                            filename = re.findall(r'\d+', msg['Subject'])[0] + ".html"                          
                            resp = "Pesanan tiket sudah Bang Joni booking.\nSilakan lakukan transaksi pembayaran tiket pesawat sejumlah %s ke: \nBank Artajasa kode institusi %s\nNo Rek: %s\nLakukan pembayaran secepatnya sebelum %s supaya tiket kamu tidak dibatalkan.\nBang Joni akan kirim tiket jika pembayaran telah diterima" % (jumlah, va_number, nomor_rekening, waktu_expired)
                            print resp
                            targetFn = self.list_fn["onEmailReceived"]
                            self.doExecCmd(lambda :targetFn(filename, resp))

                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue                               
                

                filename = part.get_filename()
                print "Attachment filename:", filename
                if filename is not None:
                    data = part.get_payload(decode=True)
                    f = open('/tmp/%s' % (filename), 'w')
                    f.write(data)
                    f.close()                           
                                       
                    if os.path.exists('/tmp/%s' % (filename)) and filename.endswith('.pdf'):
                        print "XXXX1"
                        if msg['Subject'].find("eTicket") >= 0 and msg['Subject'].find("Tiket.com") >= 0:
                            print "XXXX2"
                            filename = re.findall(r'\d+', msg['Subject'])[0] + ":" + filename  
                            print "eTicket:", filename                        
                            targetFn = self.list_fn["onEmailReceived"]
                            self.doExecCmd(lambda :targetFn(filename, "pdf"))

                        if msg['Subject'].find("Tiket Xtrans") >= 0 or msg['Subject'].find("Tiket %s" %(filename.split(".")[0])) >= 0:
                            filename = "999:" + filename  
                            print "eTicket:", filename                        
                            targetFn = self.list_fn["onEmailReceived"]
                            self.doExecCmd(lambda :targetFn(filename, "pdf"))

    def doExecCmd(self, fn):
        return fn()


    def waitForServer(self):
        logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        print "waitForServer() entered", logDtm
        
        #init
        self.newMail = False
        self.timeout = False
        self.IDLEArgs = ''
        self.stopWaitingEvent.clear()
        
        def _IDLECallback(args):
            logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            print ">A", logDtm
            self.IDLEArgs = args
            self.stopWaitingEvent.set()
            
            
        logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        print ">1", logDtm
        
        #attach callback function, and let server know it should tell us when new mail arrives    
        try:
            self.imap.idle(timeout=60*ServerTimeout, callback=_IDLECallback)
        except:
            print "set idle error"
        print(">2")


        self.stopWaitingEvent.wait()
        logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        print ">3", logDtm        
     
        if not self.killNow: # skips a chunk of code to sys.exit() more quickly.
            
            try:
                if self.IDLEArgs[0][1][0] == ('IDLE terminated (Success)'):
                    logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
                    print ">4", logDtm    
                    typ, data = self.imap.SEARCH(None, '(OR OR OR OR FROM "bambang.sso@gmail.com" FROM "noreply@tiket.com" FROM "confirmation@portal.lionair.co.id" FROM "noreply@tiketux.com" FROM "info@tiket.com" UNSEEN)') # like before, get UNSEEN message IDs
                    #typ, data = self.imap.SEARCH(None, '(OR OR OR FROM "bambang.sso@gmail.com" FROM "info@tiket.com" FROM "confirmation@portal.lionair.co.id" FROM "noreply@tiketux.com" UNSEEN)') # like before, get UNSEEN message IDs					
                
                
                    #see if each ID is new, and, if it is, make newMail True
                    for id in data[0].split():
                        if not id in self.knownAboutMail:
                            self.newMail = self.newMail or True
                        else:
                            self.timeout = True 
                        
                    if data[0] == '': # no IDs, so it was a timeout (but no notified but UNSEEN mail)
                        self.timeout = True
            except:
                    self.idleStatus = "idle_error"
                    print "IDLE terminated error"
        
            #now there has either been a timeout or a new message -- Do something...
            if self.newMail:
                self.idleStatus = "new_email"
                logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
                print "INFO: New Mail Received", logDtm
                self.showNewMailMessages()                            
            elif self.timeout:
                self.idleStatus = "timeout"
                logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
                print "INFO: A Timeout Occurred", logDtm
            
        logDtm = (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
        print "waitForServer() exited", self.idleStatus, logDtm
            

    def initCheck(self):
        typ, data = self.imap.SEARCH(None, '(OR OR OR OR FROM "bambang.sso@gmail.com" FROM "noreply@tiket.com" FROM "confirmation@portal.lionair.co.id" FROM "noreply@tiketux.com" FROM "info@tiket.com" UNSEEN)') # like before, get UNSEEN message IDs
        #typ, data = self.imap.SEARCH(None, '(OR OR OR FROM "bambang.sso@gmail.com" FROM "info@tiket.com" FROM "confirmation@portal.lionair.co.id" FROM "noreply@tiketux.com" UNSEEN)') # like before, get UNSEEN message IDs		
        newMail = False
        timeout= False            
                
        #see if each ID is new, and, if it is, make newMail True
        for id in data[0].split():
            newMail = newMail or True
                        
        if data[0] == '': # no IDs, so it was a timeout (but no notified but UNSEEN mail)
            timeout = True
        
        #now there has either been a timeout or a new message -- Do something...
        if newMail:
            print('INFO: New Mail Received')
            self.showNewMailMessages()            



    
