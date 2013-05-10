__author__ = 'dongliu'

import urllib2
import json

scheme = 'http'

album_list_base = scheme + '://picasaweb.google.com/data/feed/api/user/%s?' \
                           'alt=json&v=2&' \
                           'fields=entry(title,gphoto:id,gphoto:name,gphoto:numphotos,media:group(media:thumbnail))'
album_base = scheme + '://picasaweb.google.com/data/feed/api/user/%s/album/%s?' \
                      'alt=json&v=2&' \
                      'fields=title,openSearch:totalResults,' \
                      'entry(published,updated,title,summary,gphoto:id,gphoto:width,gphoto:height,content,media:group(media:thumbnail))'

class Album(object):
    def __init__(self):
        self.title = ''
        self.albumid = ''
        self.albumname = ''
        self.size = ''
        self.thumbnail = ''
        self.list = None

class Photo(object):
    def __init__(self):
        self.id = ''
        self.title = ''
        self.summary = ''
        self.src = ''
        self.thumbnail = ''


def geturl(url):
    response = None
    try:
        response = urllib2.urlopen(url)
        content = response.read()
        return content
    except urllib2.URLError, e:
        return None
    finally:
        if response:
            response.close()

class PicasaService(object):

    @staticmethod
    def get_album_list(userid):
        album_list = album_list_base % userid
        content = geturl(album_list)
        result = json.loads(content)
        feed = result["feed"]
        entrys = feed["entry"]
        list = []
        for entry in entrys:
            album = Album()
            album.title = entry["title"]["$t"]
            album.albumid = entry["gphoto$id"]["$t"]
            album.albumname = entry["gphoto$name"]["$t"]
            album.size = entry["gphoto$numphotos"]["$t"]
            album.thumbnail = entry["media$group"]["media$thumbnail"][0]["url"]
            list.append(album)
        return list

    @staticmethod
    def get_album(userid, albumname):
        albumurl = album_base % (userid, albumname)
        content = geturl(albumurl)
        result = json.loads(content)
        feed = result["feed"]
        album = Album()
        album.title = feed["title"]["$t"]
        album.size = feed["openSearch$totalResults"]["$t"]

        entrys = feed["entry"]
        list = []
        for entry in entrys:
            photo = Photo()
            photo.title = entry["title"]["$t"]
            photo.summary = entry["summary"]["$t"]
            photo.src = entry["content"]["src"]
            photo.id = entry["gphoto$id"]["$t"]
            photo.thumbnail = entry["media$group"]["media$thumbnail"][1]["url"]
            list.append(photo)
        album.list = list
        return album


#picasaService = PiacasaService()
#print picasaService.get_album_list("dongliu84")
#print picasaService.get_album("dongliu84", "olskIB")