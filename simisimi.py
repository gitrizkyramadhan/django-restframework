import urllib
import urllib2
import json
class SimiSimi():

    def __init__(self):

        self.key = 'de650f74-4eba-426d-a96f-e2d6f764d876'
        self.language = 'id'
        self.base_url = 'http://sandbox.api.simsimi.com/request.p'
        print "SimiSimi module added"

    def response_message(self,text):

        filter_words = 1.0
        data = {}
        data['key'] = self.key
        data['lc'] = self.language
        data['ft'] = filter_words
        data['text'] = text
        param = urllib.urlencode(data)
        url = self.base_url + '?' + param
        response = urllib2.urlopen(url)
        read_response = response.read()
        result = json.loads(read_response)
        reply_message = result['response']

        return reply_message


