from gevent import pywsgi
from flask import Flask, render_template, request, redirect
import base64

#import logging
import gevent.monkey
gevent.monkey.patch_all()

if __name__==  "__main__":
    print "Cloudmailinis online"
	
    app = Flask(__name__)

    #import logging
    #log = logging.getLogger('werkzeug')
    #log.setLevel(logging.ERROR)

    #app.logger.setLevel(log.ERROR)	
    #app.debug = True
    
    @app.route('/cloudmailin', methods=['POST'])
    def cloudmailin():
        content = request.get_json()
        to_email = content['envelope']['to']
        from_email = content['envelope']['from']
        subject_email = content['headers']['Subject']
        date_email = content['headers']['Date']
        body_email = content['plain']
        
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
        
        print "========"
        print to_email, from_email, subject_email, date_email, body_email, attach_email, content_email
        #print to_email, from_email
        return "OK"
        
   
    print "starting gevent wsgi..."   
    pywsgi.WSGIServer(('', 8002), app).serve_forever()