#encoding=utf-8

import webapp2
from service import picasa
from db.config_db import *
from tools.web_tools import *

class PicasaList(webapp2.RequestHandler):
    def get(self):
        album_list = picasa.get_album_list(Config()["picasaalbumname"])
        template_values = {
            "albumlist": album_list,
        }
        show_html(self.response, 'album_list.html', template_values)

class PicasaAlbum(webapp2.RequestHandler):
    def get(self, albumname):
        album = picasa.get_album(Config()["picasaalbumname"], albumname)
        template_values = {
            "album": album,
            }
        show_html(self.response, 'album.html', template_values)