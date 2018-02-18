# -*-coding:UTF-8 -*

from html.parser import HTMLParser
import urllib.request
import urllib.parse


class SteamParser(HTMLParser):
    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=True)
        self.name = "Aucun résultat"
        self.price = "None"
        self.release = "-"
        self.avis = "None"
        self.in_name = False
        self.in_div = False
        self.in_a = False
        self.in_release = False
        self.in_price = False

    def error(self, message):
        pass

    def reset(self):
        HTMLParser.reset(self)
        self.name = "Aucun résultat"
        self.price = "None"
        self.release = "-"
        self.avis = "None"
        self.in_name = False
        self.in_div = False
        self.in_a = False
        self.in_release = False
        self.in_price = False
    
    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for attr in attrs: 
                name, value = attr
                if name == 'id' and value == 'search_result_container':
                    self.in_div = True
                    return 
                if self.in_div and self.in_a and name == 'class' and value == 'col search_released':
                    self.in_release = True
                    return
                if self.in_div and self.in_a and name == 'class' and value == 'col search_price ':
                    self.in_price = True
                    return
        if tag == 'span':
            if self.in_a and self.in_div:
                for attr in attrs: 
                    name, value = attr
                    if name == 'data-store-tooltip':
                        self.avis = str(value).split('>')[-1]
                        return
                    if name == 'class' and value == 'title':
                        self.in_name = True
                        return
        if tag == 'a':
            if self.in_div:
                self.in_a = True
                return
            
    def handle_endtag(self, tag):
        if tag == 'span':
            if self.in_name:
                self.in_name = False
                return
        if tag == 'div':
            if self.in_release:
                self.in_release = False
                return
            if self.in_price:
                self.in_price = False
                return
        if tag == 'a':
            if self.in_div:
                self.in_a = False
                self.in_div = False
                
    def handle_data(self, data):
        if self.in_name:
            self.name = data.replace('\t','').replace('\r','').replace('\n','')
            return
        if self.in_release:
            self.release = data
            return
        if self.in_price:
            self.price = data.replace('\t','').replace('\r','').replace('\n','')#''.join([c for c in data if c.isalnum() or c == ',' or c == '€'])
            return


steam_parser = SteamParser()
print("---- steam module loaded ----")


def get_data(name):
    steam_parser.reset()
    try:
        html = urllib.request.urlopen("http://store.steampowered.com/search/?&term="+urllib.parse.quote('+'.join(name.split(' ')))).read().decode()
        html = steam_parser.unescape(html)
        steam_parser.feed(html)
    except:
        print("*** erreur url steam ***")
    return steam_parser.name, steam_parser.release, steam_parser.price, steam_parser.avis

# print(get_data("final fantasy"))
# print(get_data("sonic"))
