# -*-coding:UTF-8 -*
import json
import urllib.request
import datetime
import os
import time
import urllib.parse

geoloc_addr = "https://maps.googleapis.com/maps/api/geocode/json?language=fr&"
timez_addr = "https://maps.googleapis.com/maps/api/timezone/json?language=fr&"
search_addr = "https://www.googleapis.com/customsearch/v1?"
id_key = os.environ.get('GOOGLE_ID_KEY')

print("---- google module loaded ----")


def get_geoloc(address):
    query = "address="+urllib.parse.quote('+'.join(address.split(' ')))
    try:
        data_j = urllib.request.urlopen(geoloc_addr+query).read().decode()
        data = json.loads(data_j)['results'][0]
    except:
        print("*** erreur geoloc ***")
        return 0,0,'-1'
    geoloc = data['geometry']['location']
    return geoloc['lat'], geoloc['lng'], data['formatted_address']


def get_time_by_geoloc(address = "Paris"):
    lat, lng, name = get_geoloc(address)
    if name == '-1':
        return  'Lieu introuvable', '-', '-', '-', '-'
    query = "location="+str(lat)+","+str(lng)+"&timestamp="+str(time.time())
    try:
        data_j = urllib.request.urlopen(timez_addr+query).read().decode()
        data = json.loads(data_j)
    except:
        print("*** erreur time zone ***")
        return  'Lieu introuvable', '-', '-', '-', '-'
    timezone = datetime.timezone(datetime.timedelta(seconds=data['dstOffset']+data['rawOffset']), data['timeZoneId'])
    dt = datetime.datetime.now(timezone)
    return name, dt.hour, dt.minute, dt.second, data['timeZoneName']


def search(query):
    q = "q="+urllib.parse.quote('+'.join(query.split(' ')))+"&key="+id_key
    print(q)
    data_j = urllib.request.urlopen(search_addr+q).read().decode()
    print(data_j)
    
#print(get_time_by_geoloc("st denis, la réunion 974"))
#search("petit chaton")