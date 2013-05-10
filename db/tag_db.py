#encoding=utf-8

from google.appengine.ext import ndb
from tools.decorators import *

# default counter
CID_COUNTER = "counter"
# tag
CID_TAG = "tag"
# archive counter
CID_ARCHIVE = "archive"

# store post count
NAME_ALLPOST = "postnum"


class Tag(ndb.Model):
    cid = ndb.StringProperty()
    name = ndb.StringProperty()
    count = ndb.IntegerProperty(indexed = False)

    @staticmethod
    @cache(group="tag")
    def get_tag(cid, name):
        q = Tag.query()
        q = q.filter(Tag.cid == cid)
        q = q.filter(Tag.name == name)
        return q.get()

    @staticmethod
    @cache(group="tag")
    def get_taglist(cid):
        q = Tag.query()
        q = q.filter(Tag.cid == cid)
        return q.fetch()

    @staticmethod
    @evictgroup("tag")
    def increase(cid, name):
        tag = Tag.get_tag(cid, name)
        if tag:
            tag.count += 1
        else:
            tag = Tag()
            tag.cid = cid
            tag.name = name
            tag.count = 1
        tag.put()

    @staticmethod
    @evictgroup("tag")
    def decrease(cid, name):
        tag = Tag.get_tag(cid, name)
        if tag:
            tag.count -= 1
            if tag.count <= 0:
                tag.key.delete()
            else:
                tag.put()