import requests
import json

from geopy.distance import vincenty

APIKEY = "AIzaSyDKeRE8tRlw3cRvKmUNKHAzmsz0KOYF0QY"
BASEURL = "https://maps.googleapis.com/maps/api/geocode/json"

class GMapsGeocoding():

    def __init__(self):
        print "Load Google Maps Reverse Geocoding"

    def getLocationDetail(self, latitude, longitude):
        url = BASEURL + "?key=%s" % (APIKEY)
        url = url + "&latlng=%s,%s" % (latitude, longitude)
        print "Request :: %s" % (url)
        r = requests.get(url, headers={})
        decodedJson = json.dumps(r.json())
        decodedJson = json.loads(decodedJson)
        print "Response :: %s" % (decodedJson)
        # print decodedJson['result'][0]
        if decodedJson['status'] == 'OK':
            return self.__translateGmapData(decodedJson)

    def getLatLng(self, address):
        url = BASEURL + "?key=%s" % (APIKEY)
        # address = address.replace(" ", "+")
        url = url + "&address=%s" % (address)
        print "Request :: %s" % (url)
        r = requests.get(url, headers={})
        decodedJson = json.dumps(r.json())
        decodedJson = json.loads(decodedJson)
        print "Response :: %s" % (decodedJson)
        # print json.dumps(decodedJson['results'][0])
        if decodedJson['status'] == 'OK':
            return self.__translateGmapData(decodedJson)

    def calculateDistance(self, origin, destination):
        return vincenty(origin, destination).km

    def __translateGmapData(self, decodedJson):
        if decodedJson['status'] == 'OK':
            gmapData = decodedJson['results'][0]
            location = {}
            location['latitude'] = str(gmapData['geometry']['location']['lat'])
            location['longitude'] = str(gmapData['geometry']['location']['lng'])
            for addrObj in gmapData['address_components']:
                for admLevel in addrObj['types']:
                    if admLevel == 'administrative_area_level_4':
                        location['kelurahan'] = addrObj['long_name']
                    if admLevel == 'administrative_area_level_3':
                        location['kecamatan'] = addrObj['long_name']
                    if admLevel == 'administrative_area_level_2':
                        location['kota'] = addrObj['long_name']
                    if admLevel == 'administrative_area_level_1':
                        location['provinsi'] = addrObj['long_name']
            location['formattedAddr'] = gmapData['formatted_address']
            print location
            return location


gmaps = GMapsGeocoding()
# # gmaps.getLatLng('graha anabatic')
gmaps.getLatLng('Jl. Prof Dr Satrio No 12A, Jakarta Selatan, DKI Jakarta')
# gmaps.getLocationDetail(-6.2501281,106.5996596)