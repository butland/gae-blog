#encoding=utf-8

import webapp2
from service.fortune import *

class Fortune(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(rand_fortune())