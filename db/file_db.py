__author__ = 'dongliu'

from google.appengine.ext import ndb
from tools.decorators import *


class File(ndb.Model):
    fileName = ndb.StringProperty(indexed=False)
    mimeType = ndb.StringProperty(indexed=False)
    content = ndb.BlobProperty(indexed=False)
    date = ndb.DateTimeProperty()

    @staticmethod
    def get_files(offset, limit):
        q = File.query()
        q = q.order(-File.date)
        return q.iter(offset=offset, limit=limit)

    @staticmethod
    @cache(group="file")
    def count():
        q = File.query()
        return q.count(limit=1000)

    @staticmethod
    @cache()
    def getfile(fileid):
        return File.get_by_id(fileid)

    @staticmethod
    @evictgroup("file")
    @evictid("getfile")
    def delfile(file):
        file.key.delete()

    @staticmethod
    @evictgroup("file")
    @evictid("getfile")
    def savefile(file):
        return file.put()