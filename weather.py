import requests
import httplib2


class WeatherService() :

    def __init__(self):
        print "Weather module loaded..."

    def fetchHTML(self, url):
        connAPI = httplib2.Http()
        try:
            (resp_headers, content) = connAPI.request(url, "GET")
            # print ">>resp_header", resp_headers
            return content
        except Exception as e:
            print ">>Error is:", e

    def get_wheather(self, latitude, longitude):
        respAPI = self.fetchHTML("http://128.199.139.105/weather/weather1.php?latlong=%s,%s" % (latitude, longitude))
        weather_forecast = ""
        sqlstart = respAPI.find("<weather>")
        sqlstop = respAPI.find("</weather>") - 1
        weather_forecast = respAPI[sqlstart + 9:sqlstop]
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

            w_now = {}
            w_now['time_updated'] = time_updated
            w_now['suhu'] = suhu
            w_now['cuaca'] = cuaca
            w_now['kec_angin'] = kec_angin
            w_now['humidity'] = humidity
            w_now['image'] = self.choose_image(cuaca)

            w_tom = {}
            w_tom['cuaca'] = tom_cuaca
            w_tom['suhu_min'] = tom_suhu_min
            w_tom['suhu_max'] = tom_suhu_max
            w_tom['sunrise'] = tom_sunrise
            w_tom['sunset'] = tom_sunset
            w_tom['image'] = self.choose_image(tom_cuaca)

            return (w_now, w_tom)


    def choose_image(self, cuaca):
        cuaca = cuaca.lower().replace(' ', '_') + '.png'
        # return '' + cuaca.replace(' ', '').lower() + '.jpg'
        return 'https://bangjoni.com/weather_images/' + cuaca
