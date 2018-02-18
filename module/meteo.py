# -*-coding:UTF-8 -*

import json
import urllib.request
import urllib.parse

baseurl =  "http://api.openweathermap.org/data/2.5/weather?"

print("---- weather module loaded ----")


def get_weather(location = "France"):
    query = "q="+urllib.parse.quote(location)+"&units=metric&lang=fr"
    url = baseurl + query
    try:
        data_b = urllib.request.urlopen(url).read()
        data = json.loads(data_b.decode())
    except:
        print("*** erreur openweather ***")
        return -1
    real_name = data['name']
    temp = data['main']['temp']
    humidity = data['main']['humidity']
    pression = data['main']['pressure']
    description = data['weather'][0]['description']
    country = data['sys']['country']
    return real_name, description, temp, humidity, pression, country