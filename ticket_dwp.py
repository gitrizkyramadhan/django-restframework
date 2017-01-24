from datetime import datetime, timedelta
from decimal import Decimal
from random import randint
import re

import requests
import json
import uuid

from dbutils import DBUtil

BASE_URL_LOKET_DWP = "https://api.loket.com/v3/"
LOKET_TOKEN = "BKGzx4qeJpS44iBHCHtS3iYHZSWjyny7"
DWP_EVENT_ID = "bdd6d417335ad078cca1ff737c8d70f2"
# DWP_EVENT_ID = "9f5c824b5a6f8a879b37a2f7e6c691d4" #demo
RETRY_COUNT = 1
db = DBUtil()


# Spesific class for DWP event using loket.com API
class DWP():

    def __init__(self):
        print "DWP class loaded"
        with open('BJCONFIG.txt') as f:
            content = f.read().splitlines()
        f.close()

        self.EMAIL_NOTIF = content[9].split('=')[1]

    #refresh token if token is expired or invalid
    def refreshToken(self):
        headers = {'username': 'bangjoni', 'password': 'bangjoni77', 'APIKEY': 'ja6wHKaCETLq7m8AMZEkBThs9AmjjtEe'}
        urlToken = BASE_URL_LOKET_DWP + "login"
        r = requests.get(urlToken, headers=headers)
        decodedJson = json.dumps(r.json())
        decodedJson = json.loads(decodedJson)
        self.LOKET_TOKEN = decodedJson['data']['token']
        print "refreshing loket.com token"

    #base function to call API
    def callAPI(self, url, method, data):
        print "calling base API"
        self.refreshToken()
        urlInvoke = BASE_URL_LOKET_DWP + url
        if method == "GET":
            headers = {'token': self.LOKET_TOKEN}
            r = requests.get(urlInvoke, headers=headers)
            decodedJson = json.dumps(r.json())
        else :
            headers = {'Content-type': 'application/json', 'token': self.LOKET_TOKEN}
            r = requests.post(urlInvoke, data=json.dumps(data), headers=headers)
            decodedJson = json.dumps(r.json())
        decodedJson = json.loads(decodedJson)
        # print decodedJson
        if decodedJson["status"] == "success":
            print "call success"

            return decodedJson
        else :
            return decodedJson
            print "call failed"


    #get available events
    def getEvents(self):
        print "get events"
        responseJSON = self.callAPI("event", "GET", {})
        return responseJSON

    def getDWPEvent(self):
        responseJSON = self.getEvents()
        for event in responseJSON["data"]:
            if event["id_event"] == DWP_EVENT_ID :
                return event

    def getTicketDetail(self,ticketId,qty):
        dwpevent = self.getDWPEvent()
        for schedules in dwpevent['schedules']:
            for ticket in schedules['ticket_types']:
                # if ticket['id_ticket'] == ticketId:
                if ticket['ticket_type'].lower() == ticketId.lower():
                    return ticket

    #generate random and unique invoice code
    def randomInvoiceCode(self):
        invoiceCode = "INVBJ"
        generatedUUID = str(uuid.uuid4())
        generatedUUID = generatedUUID.replace("-","")
        dateString = str(datetime.now())
        dateString = dateString.replace("-","")
        dateString = dateString.replace(" ", "")
        dateString = dateString.replace(":", "")
        dateString = dateString.replace(".", "")
        invoiceCode = invoiceCode + dateString + generatedUUID
        return invoiceCode[:24]

    #book selected ticket
    def bookTickets(self, ticketCategory, quantity, firstName, lastName, idNumber, dob, gender, email, phone, uid, discType):
        print "ticketCategory :: " + ticketCategory + ", quantity :: " + quantity + ", firstName :: " + firstName + ", idNumber :: " + idNumber + ", dob :: " + str(dob) + ", email :: " + str(email) + ", phone :: " + str(phone) + ", uid :: " + str(uid) + ", discType :: " + discType
        errorCode = 0


        if self.checkUidTransaction(uid) == 1:
            errorCode = 1004 #user id tidak boleh double (sudah pernah transaksi)
        if discType == 1 and int(quantity) > 4:
            errorCode = 1005 #melebihi kuota tiket per orang
        if self.checkPendingUidTransaction(uid) == 1:
            errorCode = 1011  # masih ada pending transaksi dengan user yg sama
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errorCode = 1012

        ticketId = self.getTicketId(ticketCategory)
        ticketDetail = self.getTicketDetail(ticketId,quantity)

        if ticketDetail:
            #validasi tiket dari loket.com
            if int(ticketDetail['available']) < int(quantity):
                errorCode = 1001
            if ticketDetail['status_ticket'] != 'Active':
                errorCode = 1002
            if ticketDetail['is_ticket_hold'] != '0':
                errorCode = 1003

            try:
                f = "%d-%m-%Y"
                formattedDate = datetime.strptime(dob, f)
            except Exception as e:
                print e
                errorCode = 1008
        else:
            errorCode = 1001

        if errorCode == 0:
            invoiceId = self.randomInvoiceCode()
            print "book ticket"
            reqData = {
                        "data" : {
                            "tickets" :
                              [
                                    {"id_ticket": ticketDetail['id_ticket'], "qty" : quantity}
                            ],
                        "attendee"   : {
                          "firstname" : firstName,
                              "lastname" : "",
                              "identity_id" : idNumber,
                          "dob" : dob,
                          "gender" : gender,
                              "email" : self.EMAIL_NOTIF,
                              # "email" : email,
                              "telephone" : phone
                        },
                        "order_id" : invoiceId,
                        "expiration_type" : "2",
                        "notes":"ORDER FROM BANGJONI"
                        }
                }
            print json.dumps(reqData)
            responseJSON = self.callAPI("invoice/create", "POST", reqData)
            print json.dumps(responseJSON)
            ticketTotalx = Decimal(responseJSON['data']['info_summary']['ticket_totalx'].strip(' "').replace(".",""))
            amountPay = self.calculateDiscount(discType,ticketTotalx)
            sqlQuery = "INSERT INTO ticket_dwp " \
                       "(user_id, first_name, last_name, id_number, dob, gender, phone, email, invoice_id, booking_id, has_paid, order_time, book_time, amount_pay, total_amount, discount_type) VALUES " \
                       "('"+uid+"', '"+firstName+"', '"+lastName+"', '"+idNumber+"', '"+formattedDate.strftime("%Y-%m-%d")+"', '"+gender+"', '"+phone+"', '"+email+"', '"+invoiceId+"', '"+responseJSON['data']['invoice_code']+"', '0', now(), null, '"+str(amountPay)+"','"+str(ticketTotalx)+"','"+str(discType)+"') "
            db.execSQL(sqlQuery)
            print sqlQuery
            responseJSON['data']['amountpay'] = str(amountPay)
            responseJSON['data']['invoice_id'] = invoiceId
            maxBookTime = datetime.now() + timedelta(hours=4)
            responseJSON['data']['max_book_time'] = str(maxBookTime.hour) + ":" + str(maxBookTime.minute)
            return responseJSON
        else:
            return {"error_code":errorCode}

    def calculateDiscount(self, discType, totalAmount):
        if int(discType) == 0: #buy 5 gratis 1
            totalAmount = totalAmount / Decimal(6) * Decimal(5)
            totalAmount = round(totalAmount)
        else: #disc 15%
            disc = totalAmount * Decimal(15)/Decimal(100)
            totalAmount = round(totalAmount - disc)
        totalAmount = str(totalAmount)
        totalAmount = self.replaceAmountRandom(totalAmount)
        return totalAmount

    def replaceAmountRandom(self, amountStr):
        amountStr = amountStr.split(".")[0]
        head = amountStr[0:len(amountStr)-3]
        number1 = str(randint(0,9))
        number2 = str(randint(0,9))
        number3 = str(randint(0,9))
        amountStr = head+number1+number2+number3

        sqlQuery = "SELECT * FROM ticket_dwp WHERE amount_pay=" + amountStr + " and has_paid=0"
        fetchedRows = db.fetch(sqlQuery)

        if fetchedRows:
            self.replaceAmountRandom(amountStr)
        else:
            return amountStr

    def getTicketId(self,ticketCategory):
        # return ticketCategory

        if ticketCategory == "vip day 1" : return ""
        elif ticketCategory == "vip day 2" : return ""
        elif ticketCategory == "vip 2 day": return "VIP GOLD - Presale 2 Day Pass"
        elif ticketCategory == "general day 1": return "GA Presale 1-Day 1 Fri 9 Dec '16"
        elif ticketCategory == "general day 2": return "GA Presale 1-Day 2 Sat 10 Dec '16"
        elif ticketCategory == "general 2 day": return "GA Presale 3 - 2 Day Pass"
        # else: return "undefined"

    # update invoice as paid
    def updateInvoiceAsPaid(self, invoiceId, amountPay):
        #sqlQuery = "SELECT * FROM ticket_dwp WHERE booking_id='" + invoiceId + "'"
        sqlQuery = "SELECT * FROM ticket_dwp WHERE amount_pay='" + str(amountPay) + "' and has_paid=0"
        fetchedRows = db.fetch(sqlQuery)

        errorCode = 0
        if fetchedRows:
            # print str(fetchedRows[0][14])
            # print str(amountPay)
            if invoiceId == '':
                invoiceId = fetchedRows[0][10]
            if fetchedRows[0][14] > amountPay:
                errorCode = 1006 # bayarnya kurang
            elif fetchedRows[0][14] < amountPay:
                errorCode = 1007 # bayarnya lebih
        else:
            errorCode = 1009

        if errorCode == 0:
            responseJSON = self.callAPI("invoice/"+invoiceId+"/paid", "GET", {})
            print json.dumps(responseJSON)
            if responseJSON['status'] == 'success':
                sqlQuery = "UPDATE ticket_dwp SET " \
                           "book_time=now(), has_paid=1 WHERE booking_id='"+invoiceId+"' AND has_paid=0"
                db.execSQL(sqlQuery)
                # print sqlQuery
            else:
                errorCode == 1010
        return errorCode

    def checkUidTransaction(self, uid):
        sqlQuery = "SELECT * FROM ticket_dwp WHERE user_id='"+uid+"' AND has_paid=1"
        fetchedRows = db.fetch(sqlQuery)

        for row in fetchedRows:
            return 1
        return 0

    def checkPendingUidTransaction(self, uid):
        sqlQuery = "SELECT * FROM ticket_dwp WHERE user_id='"+uid+"' AND has_paid=0"
        fetchedRows = db.fetch(sqlQuery)

        for row in fetchedRows:
            return 1
        return 0


    def getUidFromBookingCode(self, bookingCode):
        sqlQuery = "SELECT * FROM ticket_dwp WHERE booking_id='" + bookingCode + "'"
        fetchedRows = db.fetch(sqlQuery)

        for row in fetchedRows:
            return str(row[1])
        return '0'

    def getUidFromAmountPay(self, amountPay):
        sqlQuery = "SELECT * FROM ticket_dwp WHERE amount_pay='" + amountPay + "' and has_paid=0"
        fetchedRows = db.fetch(sqlQuery)

        for row in fetchedRows:
            return str(row[1])
        return '0'

    def getBookingCodeFromAmountPay(self, amountPay):
        sqlQuery = "SELECT * FROM ticket_dwp WHERE amount_pay='" + amountPay + "' and has_paid=1"
        print sqlQuery
        fetchedRows = db.fetch(sqlQuery)

        for row in fetchedRows:
            return str(row[10])
        return '0'

# dwp = DWP()
# resp = dwp.bookTickets('VIP',3,'AWK','','1234567890','04-08-1993','L','agung.kurniawan@bangjoni.com','085790888049','uid',1)
# print json.dumps(resp)
# dwp.updateInvoiceAsPaid(resp['data']['invoice_code'])
# dwp.checkUidTransaction('uid')
