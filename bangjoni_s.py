from gevent import pywsgi
from flask import Flask, render_template, request, redirect
from tasks import doworker
from tasks import doloadtest
from tasks import docloudmailin
from tasks import doagentresp
from tasks import uber_authorization
from tasks import uber_send_notification
from tasks import uber_request_ride_surge
from tasks import push_billers_jatis
from tasks import updateDWPInvoice
from tasks import handlePostbackLovidovi
from tasks import depositNotification
from tasks import handlePostbackEcomm
from tasks import handle_complaint
from tasks import reversal_1pulsa
from tasks import handle_postback_tiketcom

#import logging
import gevent.monkey
import json
gevent.monkey.patch_all()

if __name__==  "__main__":
    print "Line bang joni bot personal assistant is online"

    app = Flask(__name__)

    #import logging
    #log = logging.getLogger('werkzeug')
    #log.setLevel(logging.ERROR)

    #app.logger.setLevel(log.ERROR)	
    #app.debug = True

    @app.route('/celery', methods=['GET'])
    def home():
        print "Hello from Client..."
        return "Hello World!"


    @app.route('/loadtest', methods=['GET'])
    def loadtest():
        #app.logger.warning('A warning message is sent.')
        doloadtest.delay()
        #print "Load Test..."
        return "OK"

    @app.route('/line1512v2', methods=['POST'])
    def bangjoni():
        content = request.get_json()
        print content
        doworker.delay(content)
        return "OK"

    #@app.route('/line1512', methods=['POST'])
    #def bangjoniprod():
    #    content = request.get_json()
    #    #print content
    #    doworker.delay(content)
    #    return "OK"		

    @app.route('/uber_token', methods=['GET'])
    def uber_token():
        state = request.args.get('state')
        code = request.args.get('code')
        print ""
        print "================================NEW UBER TOKEN REQUEST============================================="
        print state, code
        #g = uber_authorization(state, code)		
        uber_authorization.delay(state, code)
        #if g == "Y":
        #return redirect('https://line.me/R/ch/1475301685', code=302)	
        # return redirect('https://line.me/R/ch/1483177568', code=302)
        return redirect('https://line.me/R/ti/p/%40bangjoni', code=302)
        #else:
        #    return "OK"	

    @app.route('/uber_notified', methods=['POST'])
    def uber_notification():
        content = request.get_json()
        print ""
        print "================================NEW UBER NOTIF REQUEST======================================="
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
        uber_send_notification.delay(event_id, event_time, event_type, meta_user_id, meta_resource_id, meta_resource_type, meta_status, resource_href)
        #print "reply OK"
        return "OK"

    @app.route('/uber_surge', methods=['GET'])
    def uber_surge():
        surge_confirmation_id = request.args.get('surge_confirmation_id')
        print ""
        print "================================SURGE UBER NOTIF REQUEST======================================="
        print "surge_confirmation_id:", surge_confirmation_id
        uber_request_ride_surge.delay(surge_confirmation_id)
        return redirect('https://line.me/R/ch/1483177568', code=302)

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
        print "================================JATIS CALLBACK================================================="
        print "JATIS_CALLBACK:",trxid,merchant_name,merchant_code,payment_channel,trxstatus,chart_table,total_tagihan,total_pembayaran,trxtime
        print ">>>",content
        push_billers_jatis.delay(trxid, trxstatus, chart_table, payment_channel, trxtime)
        return "OK"

    @app.route('/cloudmailin', methods=['POST'])
    def cloudmailin():
        content = request.get_json()
        #print content
        print "================================CLOUDMAILIN REQUEST============================================="
        docloudmailin.delay(content)
        return "OK"

    @app.route('/agent_resp', methods=['POST'])
    def agentresp():
        content = request.get_json()
        #print content
        print "================================AGENT RESPONSE================================================="
        doagentresp.delay(content)
        return "OK"


    # ---------- DWP MODULE START ----------
    @app.route('/dwpconfirm', methods=['GET'])
    def dwpconfirmbooking():
        bookingId = request.args.get('bookingcode')
        amountpay = request.args.get('amountpay')
        print "================================DWP CONFIRM BOOKING================================================="
        print bookingId
        updateDWPInvoice.delay(bookingId,amountpay)
        return "OK"
    # ---------- DWP MODULE END ----------

    # ---------- LOVIDOVI MODULE START ----------
    @app.route('/lovidovichk', methods=['GET'])
    def lovipostback():
        action = request.args.get('action')
        itemId = request.args.get('itemid')
        userId = request.args.get('userid')
        itemname = request.args.get('itemname')
        # price = request.args.get('price')
        print "================================LOVIDOVI CHOOSE ITEM================================================="
        # print bookingId
        handlePostbackLovidovi.delay(itemId, userId, action, itemname, 1)
        return redirect("https://line.me/R/ti/p/%40bangjoni", code=302)
    # ---------- LOVIDOVI MODULE END ----------

    # ---------- ECOMM MODULE START ----------
    @app.route('/acceptecomm', methods=['GET'])
    def ecommpostbackinfo():
        userId = request.args.get('userid')
        merchantName = request.args.get('merchantName')
        merchantPhone = request.args.get('merchantPhone')
        merchantImg = request.args.get('merchantImg')
        # price = request.args.get('price')
        print "================================ACCEPT ORDER================================================="
        # print bookingId
        handlePostbackEcomm.delay(userId, merchantName, merchantPhone, merchantImg)
        return redirect("https://line.me/R/ti/p/%40bangjoni", code=302)
    # ---------- ECOMM MODULE END ----------


    @app.route('/deposit', methods=['GET'])
    def bjpaydeposit():
        trx_id = request.args.get('trx_id')
        print ""
        print "================================CYRUS DEPOSIT REQUEST============================================="
        print trx_id
        depositNotification.delay(trx_id)
        return "OK"


    @app.route('/complaint', methods=['GET'])
    def complaint():
        user_id = request.args.get('user_id')
        cust_name = request.args.get('cust_name')
        contact_phone = request.args.get('contact_phone')
        bjpay_phone = request.args.get('bjpay_phone')
        complaint = request.args.get('complaint')
        trx_date = request.args.get('trx_date')
        print ""
        print "================================NEW COMPLAINT============================================="
        print "user_id=" + user_id + ", cust_name=" + cust_name + ", contact_phone=" + contact_phone + ", bjpay_phone=" + bjpay_phone + ", complaint=" + complaint + ", trx_date=" + trx_date
        handle_complaint.delay(user_id, cust_name, contact_phone, bjpay_phone, complaint, trx_date)
        return redirect('https://line.me/R/ti/p/%40bangjoni', code=302)


    @app.route('/cyrusku', methods=['GET'])
    def cyrusku():
        print "================================REVERSAL CYRUS REQUEST============================================="
        trxid = request.args.get('trxid')
        partner_trxid = request.args.get('partner_trxid')
        msg = request.args.get('msg')
        if msg == "Reversal":
            result = request.args.get('result')
            msisdn = request.args.get('msisdn')
            reversal_1pulsa.delay(trxid, partner_trxid, msisdn)
        return "OK"


    @app.route('/postfltiket', methods=['POST'])
    def post_flight_tiket():
        print "================================POST FLIGHT TIKET.COM REQUEST============================================="
        content = request.get_json()
        msisdn = content['msisdn']
        form_data = content['formdata']
        flight_data = content['flight_data']
        handle_postback_tiketcom.delay(msisdn, form_data, flight_data)
        response = app.response_class(
            response=json.dumps("OK"),
            status=200,
            mimetype='application/json'
        )
        # print content
        # return redirect('https://line.me/R/ti/p/%40bangjoni', code=302)
        return response

    print "starting gevent wsgi..."
    pywsgi.WSGIServer(('', 8001), app).serve_forever()