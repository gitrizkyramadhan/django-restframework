import json
import re
from decimal import Decimal

from gmaps_geolocation import GMapsGeocoding

gmap = GMapsGeocoding()

places = [(2,"Bali"),(4,"Bandar Lampung"),(5,"Bandung"),(9,"Jabodetabek"), (9,"Jakarta")]

class CIMBModule():

    def __init__(self):
        print "CIMB Module Loaded"

    def _getKey(self, value):
        # print (value)
        if value['detail'] == None:
            return 0
        else :
            print value['distance']
            return Decimal(value['distance'])

    def getNearestATMLocation(self, latitude, longitude, **params):
        print "CIMB :: getNearestATMLocation(%s,%s)" % (latitude,longitude)

        maxLoopCount = params.get("loopCount", 3)

        # setup location and list of ATM from web
        # with open('cimb_atm.json') as f:
        #     content = f.read()
        # f.close()
        # decodedJson = json.loads(content)
        # branches = []
        # for page in decodedJson['pages'] :
        #     for result in page['results'] :
        #         branch = {}
        #         branch['name'] = result['LOCATIONH6_VALUE']
        #         if not result.has_key('LOCATIONBLOCK_VALUE'):
        #             continue
        #         branch['address'] = result['LOCATIONBLOCK_VALUE']
        #         dirtyAddr = branch['address']
        #         branch['detail'] = gmap.getLatLng(dirtyAddr)
        #         branches.append(branch)
        # print json.dumps(branches)

        # TODO call api atm location
        # with open('branch.json') as f:
        #     content = f.read().splitlines()
        # f.close()
        # decodedJson = json.loads(content[0])
        # print json.dumps(decodedJson)
        # print decodedJson
        # print decodedJson['result']['extractorData']['data'][0]['group']
        # print json.dumps(decodedJson['result']['extractorData']['data'][0]['group'])
        pLocObj = []
        # for locObj in decodedJson['result']['extractorData']['data'][0]['group'] :
        #     obj = {}
        #     obj['address'] = locObj['Location description'][0]
        #     dirtyAddr = json.dumps(obj['address']['text'])
        #     if (dirtyAddr.find('Jl.') > -1):
        #         dirtyAddr = dirtyAddr[dirtyAddr.find('Jl.'):]
        #     obj['detail'] = gmap.getLatLng(dirtyAddr)
        #     pLocObj.append(obj)
        userLocation = (Decimal(latitude), Decimal(longitude))

        with open('json-atm.json') as jsonATM:
            content = jsonATM.read().splitlines()
        atmJson = json.loads(content[0])
        for atmDetail in atmJson :
            if atmDetail['detail'] == None:
                # dirtyAddr = atmDetail['address']['text']
                # dirtyAddr = dirtyAddr + "%s" % ', DKI Jakarta'
                # atmDetail['detail'] = gmap.getLatLng(dirtyAddr)
                # print atmDetail
                continue
            else :
                atmLatLng = (Decimal(atmDetail['detail']['latitude']), Decimal(atmDetail['detail']['longitude']))
                atmDetail['distance'] = str(gmap.calculateDistance(userLocation, atmLatLng))
                pLocObj.append(atmDetail)

        pLocObj.sort(key=self._getKey)

        count = 0
        resultList = []
        for atm in pLocObj:
            count += 1
            if count > maxLoopCount:
                break
            resultList.append(atm)
        print json.dumps(resultList)
        return json.loads(json.dumps(resultList))

    def getNearestBranchLocation(self, latitude, longitude, **params):
        print "CIMB :: getNearestBranchLocation(%s,%s)" % (latitude, longitude)

        maxLoopCount = params.get("loopCount", 3)

        # setup location and list of branch from web
        # with open('cimb_branch.json') as f:
        #     content = f.read()
        # f.close()
        # decodedJson = json.loads(content)
        # branches = []
        # for page in decodedJson['pages'] :
        #     for result in page['results'] :
        #         branch = {}
        #         branch['name'] = result['LOCATIONH6_VALUE']
        #         branch['address'] = result['LOCATIONBLOCK_VALUE']
        #         dirtyAddr = branch['address']
        #         branch['detail'] = gmap.getLatLng(dirtyAddr)
        #         branches.append(branch)
        # print json.dumps(branches)

        pLocObj = []
        userLocation = (Decimal(latitude), Decimal(longitude))

        with open('json-branch.json') as f:
            content = f.read()
        f.close()
        decodedJson = json.loads(content)
        for branch in decodedJson :
            if branch['detail'] == None :
                continue
            print branch
            branchLatLng = (Decimal(branch['detail']['latitude']), Decimal(branch['detail']['longitude']))
            branch['distance'] = str(gmap.calculateDistance(userLocation, branchLatLng))
            pLocObj.append(branch)

        pLocObj.sort(key=self._getKey)

        count = 0
        resultList = []
        for branch in pLocObj :
            count += 1
            if count > maxLoopCount :
                break
            resultList.append(branch)
        print json.dumps(resultList)
        return json.loads(json.dumps(resultList))

    def getNearestPromo(self, **params):
        with open('cimb_promocc.json') as f:
            content = f.read()
        f.close()
        decodedJson = json.loads(content)
        promos = []
        for page in decodedJson['pages'] :
            for result in page['results'] :
                promocc = {}
                found = False
                if (params.has_key("location")):
                    print "LOCATION ==> "+params.get("location").lower()
                    p = re.compile('city=([^&]*)')
                    # print p.findall(page['pageUrl'])[0]
                    for key,value in places :
                        if value.lower() == params.get("location").lower():
                            if (params.has_key("merchant")):
                                print "MERCHANT ==> "+params.get("merchant").lower()
                                promoName = result['FANCYBOX.IFRAME_LINK/_title']
                                if promoName.lower().find(params.get("merchant").lower()) > -1 :
                                    found = True
                            else :
                                found = True
                    if not found :
                        continue;
                elif (params.has_key("merchant")) :
                    print "MERCHANT ==> "+params.get("merchant").lower()
                    promoName = result['FANCYBOX.IFRAME_LINK/_title']
                    if promoName.lower().find(params.get("merchant")) > -1:
                        found = True
                    if not found :
                        continue;
                promocc['name'] = result['FANCYBOX.IFRAME_LINK/_title']
                promocc['description'] = result['PEXTRAINFO_DESCRIPTION']
                promocc['image'] = result['PIMG_IMAGE']
                promocc['detailLink'] = result['FANCYBOX.IFRAME_LINK']
                promocc['sourceLink'] = page['pageUrl']
                promos.append(promocc)
        print json.dumps(promos)
        return promos
        # print "CIMB :: getNearestPromo(%s,%s)" % (params.get("latitude"), params.get("longitude"))

    def getProductInfo(self, **params):
        print ""

    def getBranchlessProduct(self, **params):
        print ""

# cimb = CIMBModule()
# cimb.getNearestBranchLocation(-6.2501281, 106.5996596)
# cimb.getNearestATMLocation(-6.2501281, 106.5996596)
# cimb.getNearestPromo(location="jakarta")
# cimb.getNearestPromo(merchant="SKAI")