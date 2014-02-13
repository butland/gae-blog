__author__ = 'dongliu'

from google.appengine.api import users

from db.configdb import *
from web import app
from flask import (redirect, request)


@app.route('/login', methods=['GET'])
def login():
    config = Config()
    referer = request.headers.get('Referer')
    if not referer:
        referer = ""
    loginurl = users.create_login_url(referer)
    return redirect(loginurl)


@app.route('/logout', methods=['GET'])
def logout():
    referer = request.headers.get('Referer')
    if not referer:
        referer = ""
    logouturl = users.create_logout_url(referer)
    return redirect(logouturl)