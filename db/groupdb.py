__author__ = 'dongliu'
#encoding=utf-8

from google.appengine.ext import ndb
from google.appengine.api import memcache


class Group(ndb.Model):
    """simulate cache group use memcached and database"""
    count = ndb.IntegerProperty(indexed=False)

    @staticmethod
    def get_group_count(group):
        key = "group#" + group
        value = memcache.get(key)
        if value is not None:
            return value

        g = Group.get_by_id(group)
        if g:
            count = g.count
        else:
            count = 0
        memcache.add(key, count)
        return count

    @staticmethod
    def increase(group):
        key = "group#" + group
        g = Group.get_by_id(group)
        if g:
            g.count = (g.count + 1) % 100000
        else:
            g = Group(id=group)
            g.count = 1
        memcache.set(key, g.count)
        g.put()
