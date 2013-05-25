#encoding=utf-8

import webapp2
import urllib
from db.filedb import *
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from datetime import datetime
from tools.webtools import show_json

CACHE_DURATION = 30 * 24 * 60 * 60 * 1000


class FileShow(webapp2.RequestHandler):
    def get(self, fileid):
        file = File.getfile(int(fileid))

        etag = "MyEtag" + str(len(file.content))

        self.response.headers['Content-Type'] = file.mimeType.encode('utf-8')
        self.response.headers['Etag'] = etag
        self.response.headers["Cache-Control"] = str(CACHE_DURATION)
        if etag == self.request.headers.get('Referer'):
            self.response.status = 304
            return

        filename = file.fileName
        if filename:
            idx = filename.rfind('/')
            if idx > 0:
                filename = filename[idx + 1:]
        self.response.headers["Content-Disposition"] = "inline; filename=" + urllib.quote(filename.encode("utf-8"))
        self.response.write(file.content)


class FileUpload(webapp2.RequestHandler):
    def post(self):
        if not users.is_current_user_admin():
            return
        utype = self.request.get("type")
        fileinfo = self.request.POST.multi['file']
        file = File()
        file.fileName = fileinfo.filename
        file.mimeType = fileinfo.type
        file.content = fileinfo.value
        file.date = datetime.today()
        fileid = File.savefile(file).id()
        if utype == 'redactor_img':
            # for redactor call back
            self.response.headers["Content-Type"] = "text/html; charset=UTF-8"
            self.response.headers["Cache-Control"] = "no-cache";

            self.response.write('{"filelink": "/showfile/%d"}' % fileid)
        elif utype == 'redactor_file':
            # for redactor call back
            self.response.headers["Content-Type"] = "text/html; charset=UTF-8"
            self.response.headers["Cache-Control"] = "no-cache";
            self.response.write('{ "filelink": "/showfile/%d", "filename": "%s" }' % (fileid, fileinfo.filename))
        else:
            # now it is not used.
            self.redirect('/admin/file')


class FileDelete(webapp2.RequestHandler):
    def post(self):
        fileid = int(self.request.get("fileid"))
        file = File.getfile(fileid)
        File.delfile(file)
        show_json(self.response, {'state': 0, 'msg': ''})


class BlobShow(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blobkey):
        resource = str(urllib.unquote(blobkey))
        blob_info = blobstore.BlobInfo.get(resource)
        self.response.headers["Cache-Control"] = str(CACHE_DURATION)
        self.send_blob(blob_info)