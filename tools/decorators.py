__author__ = 'dongliu'
from google.appengine.api import memcache
from db.group_db import *


def tostr(arg):
    if type(arg) == type(u''):
        return arg.encode('utf-8')
    else:
        return str(arg)


def _get_key(group, name, args, kwargs):
    # for get by id cache
    if group == '':
        key = name + '#' + str(args[0])
        return key
    key = name + str(Group.get_group_count(group))
    key += '#' + '-'.join([tostr(arg) for arg in args])
    dkeys = kwargs.keys()
    dkeys.sort()
    key += '#' + '-'.join([dkey + '_' + str(kwargs[dkey]) for dkey in dkeys])
    return key


def cache(group):
    def _cache(function):
        def wrapper(*args, **kwargs):
            key = _get_key(group, function.__name__, args, kwargs)
            value = memcache.get(key)
            if value is not None:
                return value
            else:
                value = function(*args, **kwargs)
                memcache.set(key, value = value, time = 3600*24)
                return value
        return wrapper
    return _cache


def evictgroup(group):
    def _evictgroup(function):
        def wrapper(*args, **kwargs):
            value = function(*args, **kwargs)
            Group.increase(group)
            return value
        return wrapper
    return _evictgroup


def evict(name):
    def _evict(function):
        def wrapper(*args, **kwargs):
            key = _get_key("", name, args, kwargs)
            value = function(*args, **kwargs)
            memcache.delete(key)
            return value
        return wrapper
    return _evict


def evictid(name):
    def _evict(function):
        def wrapper(*args, **kwargs):
            if args[0].key is not None:
                key = _get_key("", name, (args[0].key.id(), ), kwargs)
                value = function(*args, **kwargs)
                memcache.delete(key)
            else:
                value = function(*args, **kwargs)
            return value
        return wrapper
    return _evict


def singleton(cls, *args, **kw):
    instances = {}
    def wrapper():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return wrapper