#encoding=utf-8

import webapp2
import StringIO
from tools import captcha
from google.appengine.api import memcache
from tools.web_tools import *

class Captcha(webapp2.RequestHandler):
    """
    show captcha test.
    """
    def get(self):
        seq = self.request.get('seq')
        self.response.headers['Content-Type'] = 'image/gif'
        mstream = StringIO.StringIO()
        code_img, code = captcha.create_validate_code()
        memcache.add(key = "captcha#"+seq, value = code, time = 3600)
        code_img.save(mstream, "GIF")
        self.response.out.write(mstream.getvalue())

class CaptchaCheck(webapp2.RequestHandler):
    def post(self):
        seq = self.request.get('seq')
        code = self.request.get('code')
        if not seq or not code:
            show_json(self.response, {"state" : -1})
            return
        ocode = memcache.get("captcha#"+seq)
        if not ocode or code.strip().upper() != ocode:
            show_json(self.response, {"state" : 1})
            return
        show_json(self.response, {"state" : 0})