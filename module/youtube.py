# -*-coding:UTF-8 -*

from html.parser import HTMLParser
import urllib.request
import json
import os
import re
import datetime

youtubeURL = "https://www.googleapis.com/youtube/v3/videos?"
id_key = os.environ.get('YOUTUBE_ID_KEY')

class YoutubeParser(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self.title = "No video"
        self.views = "0"
        self.date = ""
        self.in_div = False
        self.in_date = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for attr in attrs:
                name, value = attr
                if name == 'class' and value == 'watch-view-count':
                    self.in_div = True
                    return
        if tag == 'span':
            for k, v in attrs:
                if k == 'id' and v == 'eow-title':
                    for k,v in attrs:
                        if k == 'title':
                            self.title = v;
                            return
        if tag == 'strong':
            for k, v in attrs:
                if k  == 'class' and v == "watch-time-text":
                    self.in_date = True
        
    def handle_endtag(self, tag):
        if tag == 'div':
            if self.in_div:
                self.in_div = False
        if tag == 'strong':
            if self.in_date:
                self.in_date = False
        
    def handle_data(self, data):
        if self.in_div:
            self.views = data
        if self.in_date:
            self.date = data
       
yt_parser = YoutubeParser() 
print("---- youtube module loaded ----")

def get_video(video_id):
    request = youtubeURL+"part=statistics,snippet"+"&id="+video_id+"&key="+id_key
    data_j = urllib.request.urlopen(request).read().decode()
    data = json.loads(data_j)["items"][0]
    return data["snippet"]["title"], data["statistics"]["viewCount"], datetime.datetime.strptime(data["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%m-%Y")
    
def retrieve_id(url):
    m = re.search("v=((\w|-)+)", url)
    return m.group(1)

def get_title_and_views(url):
    yt_parser.reset()
    try:
        #html = urllib.request.urlopen(url).read().decode()
        #yt_parser.feed(html)
        id_video = retrieve_id(url)
        return get_video(id_video)
    except:
        print("*** erreur url youtube ***")
    if yt_parser.views.split('\xa0')[-1] == "vues":
        yt_parser.views = yt_parser.views.split('\xa0')[0]
    return yt_parser.title, yt_parser.views, yt_parser.date

#print(get_title_and_views_0("https://www.youtube.com/watch?v=cJQwnAhXnBk&list=PLrA8DJCeLT55EUwurwrMHiEDqZrsS8TGJ&index=10"))
#print(get_title_and_views("https://www.youtube.com/watch?v=cJQwnAhXnBk&list=PLrA8DJCeLT55EUwurwrMHiEDqZrsS8TGJ&index=10"))
#print(get_title_and_views("https://www.youtube.com/watch?v=WQvM4EM0lO8"))
#print(get_title_and_views("https://www.youtube.com/watch?v=N-aK6JnyFmk"))
#print(get_title_and_views("https://www.youtube.com/watch?v=N-aK6JnyFmk&list=RD0sB3Fjw3Uvc&index=2"))
#print(get_title_and_views("https://www.youtube.com/watch?v=u2hYn_4yuhc"))

#print(get_video("qmsbP13xu6k"))