#encoding=utf-8

__author__ = 'dongliu'

import urllib
from db.filedb import *
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from datetime import datetime
from web import app
from flask import (request, send_file, jsonify, make_response, abort, redirect)

CACHE_DURATION = 24 * 60 * 60 * 1000


@app.route('/showfile/<int:fileid>', methods=['GET'])
@app.route('/showimage/<int:fileid>', methods=['GET'])
def show_file(fileid):
    #TODO: add condition reqeust.
    file = File.getfile(fileid)

    if not file:
        abort(404)

    filename = file.fileName
    if filename:
        idx = filename.rfind('/')
        if idx > 0:
            filename = filename[idx + 1:]

    resp = make_response(file.content, 200)
    resp.headers['Content-Type'] = file.mimeType.encode('utf-8')
    resp.headers["Cache-Control"] = str(CACHE_DURATION)
    resp.headers["Content-Disposition"] = "inline; filename=" + urllib.quote(filename.encode("utf-8"))
    return resp


@app.route('/file/upload', methods=['POST'])
def upload_file():
    if not users.is_current_user_admin():
        abort(403)
    utype = request.values.get("type")
    fileinfo = request.files['file']
    file = File()
    file.fileName = fileinfo.filename
    file.mimeType = fileinfo.mimetype
    file.content = fileinfo.getvalue()
    file.date = datetime.today()
    fileid = File.savefile(file).id()
    if utype == 'redactor_img':
        # for redactor img update call back
        return jsonify({"filelink": "/showfile/%d" % fileid})
    elif utype == 'redactor_file':
        # for redactor file upload call back
        return jsonify({"filelink": "/showfile/%d" % fileid, "filename": fileinfo.filename})
    else:
        # now it is not used.
        return redirect('/admin/file')


@app.route('/file/delete', methods=['POST'])
def delete_file():
    fileid = int(request.values.get("fileid"))
    file = File.getfile(fileid)
    File.delfile(file)
    return jsonify({'state': 0, 'msg': ''})