# -*-coding:UTF-8 -*

from html.parser import HTMLParser
import json
import urllib.request


class ForumParser(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self.title = "Topic introuvable"
        self.in_title = False
        
    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
            return
        
    def handle_endtag(self, tag):
        if self.in_title:
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title = data.replace('\t','').replace('\r','').replace('\n','')


class CFMParser(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self.mods = {}
        self.admin = []
        self.current_id = ""
        self.in_r = False
        self.in_mod = False
        self.is_admin = False
        self.in_id = False
        
    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            for attr in attrs:
                name, value = attr
                if name == 'class' and (value == "lb1" or value == "lb2"):
                    self.in_r = True
                    return
        if tag == "b":
            if self.in_r:
                self.in_id = True
                return
        if tag == 'a':
            if self.in_r: 
                self.in_mod = True
                for attr in attrs:
                    name, value = attr
                    if name == 'class' and value == 'admin_mouse':
                        self.is_admin = True
                return
        
    def handle_data(self, data):
        if self.in_id:
            self.current_id = data
            self.mods.setdefault(data, [])
            return
        if self.in_mod:
            self.mods[self.current_id].append(data)
            if self.is_admin:
                self.admin.append(data)
            return
        
    def handle_endtag(self, tag):
        if tag == 'b':
            if self.in_id:
                self.in_id = False
                return
        if tag == 'a':
            if self.in_mod:
                self.in_mod = False
            if self.is_admin:
                self.is_admin = False
            return
        if tag == 'tr':
            if self.in_r:
                self.in_r = False
                return 


cfm_parser = CFMParser()
forum_parser = ForumParser()
print("---- transfo module loaded ----")


def get_online_mods():
    cfm_parser.reset()
    try:
        html = urllib.request.urlopen("http://cheese.formice.com/online-mods").read().decode()
        cfm_parser.feed(html)
    except:
        print("*** échec mods cfm ***")
    return cfm_parser.mods, cfm_parser.admin


def get_mapcrew():
    try:
        html = urllib.request.urlopen("http://api.formice.com/mapcrew/online.json").read().decode()
        mapcrew = json.loads(html)
    except:
        mapcrew = {}
        print("*** echec du chargement mapcrew ***")
    return mapcrew


def get_sentinelle():
    try:
        html = urllib.request.urlopen("http://api.formice.com/sentinel/online.json").read().decode()
        sentis = json.loads(html)
    except:
        sentis = {}
        print("*** echec du chargement sentinelles ***")
    return sentis


def get_topic_title(url):
    forum_parser.reset()
    try:
        html = urllib.request.urlopen(url).read().decode()
        html = forum_parser.unescape(html)
        forum_parser.feed(html)
    except:
        print("*** échec tfm forum ***")
    return forum_parser.title


# reg1 = /<a href="section\?f=([^\"]*)&s=([^\"]*)" class=" "><img src="[^\"]*" alt="" class="espace-2-2 img16"><img src="\/img\/pays\/([^\"]*)\.png" class="img16 espace-2-2" \/>([^\"]*) <\/a>  <\/li><li><span class="divider"> \/ <\/span>  <\/li>  <li>        <a href="topic\?f=([^&]*)&t=([^\"]*)" class=" active">(?:<img src="\/img\/icones\/[^\"]*" class="img16 espace-2-2" \/>)([^<]*)<\/a>/i
# reg2 = /<a href="section\?f=([^\"]*)&s=([^\"]*)" class=" "><img src="[^\"]*" alt="" class="espace-2-2 img16"><img src="\/img\/pays\/([^\"]*)\.png" class="img16 espace-2-2" \/>([^\"]*) <\/a>  <\/li><li><span class="divider"> \/ <\/span>  <\/li>  <li>        <a href="topic\?f=([^&]*)&t=([^\"]*)" class=" active">([^<]*)<\/a>/i

# print(get_sentinelle()["fr"])
# print(get_online_mods())
