#encoding=utf-8
__author__ = 'dongliu'

from flask import (render_template, request, jsonify)
from web import app
from service import picasa
from db.configdb import Config


@app.route('/album', methods=['GET'])
def album_list():
    album_list = picasa.get_album_list(Config()["picasaalbumname"])
    return render_template('album_list.html', albumlist=album_list, config=Config())


@app.route('/album/<albumname>/', methods=['GET'])
def show_search(albumname):
    album = picasa.get_album(Config()["picasaalbumname"], albumname)
    return render_template('gallery.html', album=album, config=Config())