__author__ = 'dongliu'

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
    @cache(name="file-${fileid}")
    def getfile(fileid):
        return File.get_by_id(fileid)

    @staticmethod
    @evictgroup("file")
    @evict(name="file-${f}")
    def delfile(f):
        f.key.delete()

    @staticmethod
    @evictgroup("file")
    @evict(name="file-${f}")
    def savefile(f):
        return f.put()