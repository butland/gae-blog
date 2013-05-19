#encoding=utf-8

import webapp2
from google.appengine.api import users
from db.config_db import *


class Login(webapp2.RequestHandler):
    def get(self):
        config = Config()
        referer = self.request.headers.get('Referer')
        if not referer:
            referer = "";
        loginurl = users.create_login_url(referer)
        self.redirect(loginurl)


class Logout(webapp2.RequestHandler):
    def get(self):
        referer = self.request.headers.get('Referer')
        if not referer:
            referer = "";
        logouturl = users.create_logout_url(referer)
        self.redirect(logouturl)