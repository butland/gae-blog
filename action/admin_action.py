#coding=utf8
__author__ = 'dongliu'

import webapp2
from db.configdb import *
from db.filedb import *
from db.postdb import *
from tools.webtools import *
from tools.pagertool import *
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
        filelist = File.get_files((page - 1) * pagesize, pagesize)
        template_values = {
            "filelist": filelist,
            "pager": pager,
        }
        show_html(self.response, '/admin/file.html', template_values)


class AdminPost(webapp2.RequestHandler):
    """admin hidden post"""
    def get(self):
        if not users.is_current_user_admin():
            return
        try:
            page = int(self.request.get('page'))
        except:
            page = 1
        total = Post.count(PRIVILEGE_HIDE)
        pagesize = 20
        pager = Pager(total, page, pagesize)
        pager.setbase('/admin/post?page=')
        postlist = Post.get_postlist(PRIVILEGE_HIDE, (page - 1) * pagesize, pagesize)
        template_values = {
            "postlist": postlist,
            "pager": pager,
            }
        show_html(self.response, '/admin/post.html', template_values)