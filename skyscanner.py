import requests
import json
from datetime import date, datetime, timedelta
# from dateutil.relativedelta import relativedelta

APIKEY = 'ba616238434893123338551586683135'
BASE_URL = 'http://partners.api.skyscanner.net/apiservices/'

class SkyscannerSDK():
    def __init__(self):
        print "SkyscannerSDK class loaded"

    def getLivePricing(self, **params):
        headers = {'Content-Type': 'application/x-www-form-urlencoded;  charset=UTF-8', 'Accept': 'application/json',
                   'Cache-Control': 'no-cache'}
        # urlSession = BASE_URL + "pricing/v1.0/" + "?apikey="+APIKEY
        urlSession = BASE_URL + "pricing/v1.0/"
        data = ''
        for key, value in params.iteritems():
            data += str(key) + '=' + str(value) + '&'
        data = data[:len(data) - 1]
        print data
        r = requests.post(urlSession, params={"apikey": APIKEY}, data=data, headers=headers)

        r.headers
        print r.headers

        urlLivePrice = r.headers.get("location")
        r = requests.get(urlLivePrice, params={"apikey": APIKEY})

        print json.dumps(r.json())
        return json.loads(json.dumps(r.json()))
        # respHeaders = json.load(r.headers)
        # print respHeaders
        # return

    def getLowestDestinationPrice(self, origin, destination):
        # six_months = date.today() + relativedelta(months=+6)
        # formatted_date = (six_months).strftime('%Y-%m')
        url = "http://partners.api.skyscanner.net/apiservices/browsequotes/v1.0/id/IDR/id-ID/"+origin+"/"+destination+"/anytime"
        # url = "http://partners.api.skyscanner.net/apiservices/browsequotes/v1.0/id/IDR/id-ID/ID/ID/anytime"
        r = requests.get(url, params={"apikey": APIKEY})
        decodedJson = json.loads(json.dumps(r.json()))

        lowest_price = 9999999999999999
        quote_id = 9999999999999999
        for quote in decodedJson['Quotes'] :
            # print quote
            # print str(lowest_price) + " > " + str(quote['MinPrice']) + " = " + str(int(lowest_price) < int(quote['MinPrice']))
            if int(lowest_price) > int(quote['MinPrice']) :
                quote_id = int(quote['QuoteId'])
                lowest_price = int(quote['MinPrice'])
        # print quote_id, lowest_price
        for quote in decodedJson['Quotes']:
            if int(quote['QuoteId']) == quote_id :
                return quote

    def getTop10CheapestPrice(self, **params):
        headers = {'Content-Type': 'application/x-www-form-urlencoded;  charset=UTF-8', 'Accept': 'application/json'}
        # urlSession = BASE_URL + "pricing/v1.0/" + "?apikey="+APIKEY
        urlSession = BASE_URL + "pricing/v1.0/"
        data = ''
        for key, value in params.iteritems():
            data += str(key) + '=' + str(value) + '&'
        data = data[:len(data) - 1]
        print data
        r = requests.post(urlSession, params={"apikey": APIKEY}, data=data, headers=headers)
        print r

        r.headers
        print r.headers

        params['apikey'] = APIKEY
        urlLivePrice = r.headers.get("location")
        while True:
            r = requests.get(urlLivePrice, params=params)
            print r
            if r.status_code == 304:
                continue
            else:
                break

        if r.json() == None:
            return

        decodedJson = json.loads(json.dumps(r.json()))
        # print decodedJson

        count = 0
        itenaries = []
        agents = decodedJson['Agents']
        segments = decodedJson['Segments']
        carriers = decodedJson['Carriers']
        places = decodedJson['Places']
        legs = decodedJson['Legs']

        # with open('airlines-logo.json') as f:
        #     content = f.read()
        # f.close()
        # airlineLogoJson = json.loads(content)

        for itenaryTemp in decodedJson['Itineraries']:
            count += 1
            if count > 5:
                break
            itenary = {}
            for agent in agents:
                if agent['Id'] == itenaryTemp['PricingOptions'][0]['Agents'][0]:
                    itenary['agentName'] = agent['Name']
                    itenary['agentImageUrl'] = agent['ImageUrl']
            itenary['outboundLegId'] = itenaryTemp['OutboundLegId']
            if 'InboundLegId' in itenaryTemp:
                itenary['inboundLegId'] = itenaryTemp['InboundLegId']
            itenary['price'] = itenaryTemp['PricingOptions'][0]['Price']
            itenary['deepLink'] = itenaryTemp['PricingOptions'][0]['DeeplinkUrl']
            for leg in legs:
                if leg['Id'] == itenary['outboundLegId']:
                    itenary['arrivalTime'] = leg['Arrival']
                    itenary['departureTime'] = leg['Departure']
                    itenary['stops'] = len(leg['Stops'])
                    itenary['duration'] = leg['Duration']

                    carrierName = ""
                    flightNumber = ""
                    carrierCommonName = ""
                    for flightNum in leg['FlightNumbers']:
                        for carrier in carriers:
                            if carrier['Id'] == flightNum['CarrierId']:
                                # logoFound = False
                                # for value in airlineLogoJson:
                                #     if value['iataCode'] == carrier['Code']:
                                #         carrierLogoURL = value
                                #         logoFound = True
                                #         break
                                # if not logoFound:
                                #     carrierLogoURL = {'url' : 'https://www.bangjoni.com/skyscanner/images/logo/image_na.png' }
                                # carrierLogoURL = 'http://logos.skyscnr.com/images/airlines/'+carrier['Code']+'.png'
                                carrierLogoURL = carrier['ImageUrl']
                                carrierName += carrier['Code'] + '-' + flightNum['FlightNumber'] + ','
                                flightNumber += flightNum['FlightNumber'] + ','
                                carrierCommonName += carrier['Name'] + ','

                    # print carrierName, flightNumber
                    itenary['flightNumbers'] = {'flightNumber': flightNumber[:len(flightNumber) - 1],
                                                'carriers': carrierName[:len(carrierName) - 1],
                                                'carrierCommonName': carrierCommonName[:len(carrierCommonName) - 1],
                                                'airlineLogo': carrierLogoURL}


                if itenary.has_key('inboundLegId'):
                    if leg['Id'] == itenary['inboundLegId']:
                        itenary['inbound_arrivalTime'] = leg['Arrival']
                        itenary['inbound_departureTime'] = leg['Departure']
                        itenary['inbound_stops'] = len(leg['Stops'])
                        itenary['inbound_duration'] = leg['Duration']

                        carrierName = ""
                        flightNumber = ""
                        carrierCommonName = ""
                        for flightNum in leg['FlightNumbers']:
                            for carrier in carriers:
                                if carrier['Id'] == flightNum['CarrierId']:
                                    # logoFound = False
                                    # for value in airlineLogoJson:
                                    #     if value['iataCode'] == carrier['Code']:
                                    #         carrierLogoURL = value
                                    #         logoFound = True
                                    #         break
                                    # if not logoFound:
                                    #     carrierLogoURL = {'url' : 'https://www.bangjoni.com/skyscanner/images/logo/image_na.png' }
                                    # carrierLogoURL = 'http://logos.skyscnr.com/images/airlines/'+carrier['Code']+'.png'
                                    carrierLogoURL = carrier['ImageUrl']
                                    carrierName += carrier['Code'] + '-' + flightNum['FlightNumber'] + ','
                                    flightNumber += flightNum['FlightNumber'] + ','
                                    carrierCommonName += carrier['Name'] + ','

                        # print carrierName, flightNumber
                        itenary['inbound_flightNumbers'] = {'flightNumber': flightNumber[:len(flightNumber) - 1],
                                                    'carriers': carrierName[:len(carrierName) - 1],
                                                    'carrierCommonName': carrierCommonName[:len(carrierCommonName) - 1],
                                                    'airlineLogo': carrierLogoURL}


                # for place in places:
                #     if place['Id'] == leg['DestinationStation']:
                #         itenary['destination'] = place['Code']
                #         itenary['destinationName'] = place['Name']
                #     if place['Id'] == leg['DestinationStation']:
                #         itenary['origin'] = place['Code']
                #         itenary['originName'] = place['Name']
            itenary['destination'] = decodedJson['Query']['DestinationPlace']
            itenary['origin'] = decodedJson['Query']['OriginPlace']
            # print itenary
            itenaries.append(itenary)
        # print json.dumps(itenaries)
        return json.loads(json.dumps(itenaries))

sk = SkyscannerSDK()
# sk.getTop10CheapestPrice(currency='IDR', locale='id-ID', originplace='CGK', destinationplace='SUB', outbounddate='2017-01-01', adults=2, country='id', locationschema='Iata', outbounddeparttime='M')
print sk.getLowestDestinationPrice('CGK','KNO')
# top_4_destinations = "CGK-KNO,CGK-SUB,CGK-DPS,CGK-LOP"
# for sky_resp_obj in top_4_destinations.split(','):
#     print sky_resp_obj