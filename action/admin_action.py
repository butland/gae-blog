#coding=utf8
__author__ = 'dongliu'

import webapp2
from db.config_db import *
from db.file_db import *
from tools.web_tools import *
from tools.pager_tool import *
from google.appengine.api import users


class AdminConfig(webapp2.RequestHandler):
    def get(self):
        if not users.is_current_user_admin():
            return
        config = Config()
        template_values = {
            "config" : config,
        }
        show_html(self.response, '/admin/config.html', template_values)
    def post(self):
        if not users.is_current_user_admin():
            return
        config = Config()
        for key in config.keys():
            value = self.request.get(key)
            if key is not None and value is not None:
                ov = config[key]
                if type(ov) == type(u''):
                    ov = ov.encode('utf-8')
                if value != str(ov):
                    config[key] = value
        self.redirect("/admin/config")


class AdminFile(webapp2.RequestHandler):
    def get(self):
        if not users.is_current_user_admin():
            return
        try:
            page = int(self.request.get('page'))
        except:
            page = 1
        total = File.count()
        pagesize = 20
        pager = Pager(total, page, pagesize)
        pager.setbase('/admin/file?page=')
        file_list = File.get_files((page-1)*pagesize, pagesize)
        template_values = {
            "filelist": file_list,
            "pager": pager,
        }
        show_html(self.response, '/admin/file.html', template_values)