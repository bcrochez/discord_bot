# -*-coding:UTF-8 -*

import json, os, sys
import urllib.request

print("---- start loading tanks data ----")
application_id = os.environ.get('WOT_APP_ID')

path = os.path.dirname(sys.argv[0])

tanks_b = b''
tank_json = ''
tank_list = {}
tank_list_sort = {}

game_version = '0'
tanks_update = '0'

try:
    file_version = open(path+'/module/wot/version.txt', 'r')
    game_version = file_version.readline().strip()
    tanks_update = file_version.readline().strip()
    file_version.close()
except:
    game_version = '0'
    tanks_update = '0'

data = urllib.request.urlopen("http://api.worldoftanks.eu/wot/encyclopedia/info/?application_id="+application_id+"&language=fr&fields=game_version,tanks_updated_at").read().decode()
version = json.loads(data)["data"]

if version["tanks_updated_at"] > int(tanks_update):
    print("  -- nouvelle version disponible! --")
    game_version = version["game_version"]
    tanks_update = str(version["tanks_updated_at"])
    
    file_version = open(path+'/module/wot/version.txt', 'w+')
    file_version.write(game_version+'\n')
    file_version.write(tanks_update+'\n')
    file_version.close()
    
    tanks_b = urllib.request.urlopen("http://api.worldoftanks.eu/wot/encyclopedia/tanks/?application_id="+application_id+"&language=fr").read().decode()
    tank_list = json.loads(tanks_b)["data"]
    tanks_file = open(path+'/module/wot/tank_list.txt', 'w+') 
    json.dump(tank_list, tanks_file)
    tanks_file.close()
else:
    print("  -- pas de nouvelle version --")
    tanks_file = open(path+'/module/wot/tank_list.txt')
    tank_list = json.load(tanks_file)
    tanks_file.close()
    
# print(tank_list)
for tank in tank_list:
    tmp = tank_list[tank]
    #print(tmp)
    if tmp["nation_i18n"] not in tank_list_sort:
        tank_list_sort[tmp["nation_i18n"]] = {}
    if tmp["type_i18n"] not in tank_list_sort[tmp["nation_i18n"]]:
        tank_list_sort[tmp["nation_i18n"]][tmp["type_i18n"]] = []
    tank_list_sort[tmp["nation_i18n"]][tmp["type_i18n"]].append(tank)

print("---- tanks data loaded ----")
#print(len(tank_list))

#data_b = urllib.request.urlopen("https://api.worldoftanks.eu/wot/account/list/?application_id="+application_id+"&search=Tanktorze").read()
#data = json.loads(data_b.decode())
#player_id = str(data["data"][0]["account_id"])
#player_data_b = urllib.request.urlopen("https://api.worldoftanks.eu/wot/account/info/?application_id="+application_id+"&account_id="+player_id).read()
#player_data = json.loads(player_data_b.decode())


def get_common_data(player_name):
    data_b = urllib.request.urlopen("https://api.worldoftanks.eu/wot/account/list/?application_id="+application_id+"&search="+player_name).read()
    data = json.loads(data_b.decode())

    player_id = str(data["data"][0]["account_id"])

    player_data_b = urllib.request.urlopen("https://api.worldoftanks.eu/wot/account/info/?application_id="+application_id+"&account_id="+player_id).read()
    player_data = json.loads(player_data_b.decode())["data"][player_id]
    
    nickname = player_data["nickname"]
    nb_battles = player_data["statistics"]["all"]["battles"]
    nb_wins = player_data["statistics"]["all"]["wins"]
    nb_frags = player_data["statistics"]["all"]["frags"]
    max_frags = player_data["statistics"]["all"]["max_frags"]
    max_dmg = player_data["statistics"]["all"]["max_damage"]
    return nickname, nb_battles, nb_wins, nb_frags, max_frags, max_dmg


def get_info_tank(tank_name):
    for tank_id in tank_list:
        if tank_list[tank_id]["short_name_i18n"].lower() == tank_name.lower():
            tank_details = tank_list[tank_id]
            #tank_id = str(tank_data["tank_id"])
            #tank_details_b = urllib.request.urlopen("http://api.worldoftanks.eu/wot/encyclopedia/tankinfo/?application_id="+application_id+"&tank_id="+tank_id).read()
            #tank_details = json.loads(tank_details_b.decode())["data"][tank_id]
            #print(tank_details)
            name = tank_details["name_i18n"]
            nation = tank_details["nation_i18n"]
            type_ = tank_details["type_i18n"].lower()
            
            try:
                tank_info = get_tank_details(tank_id)
            except: 
                return name, nation, type_, "Description introuvable"
            #weight = str(tank_details["weight"])
            return name, nation, type_, tank_info["description"]


def get_tank_list_s():
    return tank_list_sort


def get_tank_list():
    return tank_list


def get_tank_details(tank_id):
    tank_info = json.loads(urllib.request.urlopen("http://api.worldoftanks.eu/wot/encyclopedia/vehicles/?application_id="+application_id+"&language=fr&tank_id="+tank_id).read().decode())["data"][tank_id]
    return tank_info

#print(get_tank_details("9249")["next_tanks"])