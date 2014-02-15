#coding=utf8
__author__ = 'dongliu'

from google.appengine.api import users

from db.configdb import *
from db.filedb import *
from db.postdb import *
from tools.pagertool import *
from flask import (render_template, redirect, request, abort)
from web import app


@app.route('/admin/config', methods=['GET'])
def config():
    if not users.is_current_user_admin():
        abort(403)
    return render_template('admin/config.html', config=Config())


@app.route('/admin/config', methods=['POST'])
def update_config():
    if not users.is_current_user_admin():
        abort(403)
    config = Config()
    for key in config.keys():
        value = request.values.get(key)
        if key is not None and value is not None:
            ov = config[key]
            if type(ov) == type(u''):
                ov = ov.encode('utf-8')
            if value != str(ov):
                config[key] = value
    return redirect("/admin/config")


@app.route('/admin/file', methods=['GET'])
def filelist():
    if not users.is_current_user_admin():
        abort(403)
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    total = File.count()
    pagesize = 20
    pager = Pager(total, page, pagesize)
    pager.setbase('/admin/file?page=')
    filelist = File.get_files((page - 1) * pagesize, pagesize)
    return render_template('/admin/file.html', filelist=filelist, pager=pager, config=Config())


@app.route('/admin/post', methods=['GET'])
def get():
    """admin hidden post"""
    if not users.is_current_user_admin():
        return
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    total = Post.count(PRIVILEGE_HIDE)
    pagesize = 20
    pager = Pager(total, page, pagesize)
    pager.setbase('/admin/post?page=')
    postlist = Post.get_postlist(PRIVILEGE_HIDE, (page - 1) * pagesize, pagesize)
    return render_template('/admin/post.html', postlist=postlist, pager=pager, config=Config())