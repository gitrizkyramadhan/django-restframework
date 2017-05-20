import urllib
import urllib2
import json
class SimiSimi():

    def __init__(self):

        self.key = '1d3f6082-d7c8-471a-977b-e0e5a31530ca'
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
        if result == 100:
            reply_message = result['response']
            filter_message = reply_message.lower().replace('simi' , 'abang')
        else:
            filter_message = 'apaan sih'
        return filter_message


# sm = SimiSimi()
# print sm.response_message('kuontooolll')