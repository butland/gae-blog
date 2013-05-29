__author__ = 'dongliu'
from google.appengine.api import memcache
from db.groupdb import *
import inspect
import itertools
from string import Template


def tostr(arg):
    if type(arg) == type(u''):
        return arg.encode('utf-8')
    else:
        return str(arg)


def _getkey(group, name, functionname, argsdict):
    if name:
        t = Template(name)
        key = t.substitute(argsdict)
    else:
        # this is evil, and not well controled, so always give a name.
        key = functionname
        if argsdict:
            argslist = sorted(argsdict.items(), key=lambda t: t[0])
            key = key + '-' + '-'.join([t[1] for t in argslist])

    if group:
        key = '%s-%d#%s' % (group, Group.get_group_count(group), key)
    return key


def _parsefunction(function, args, kwargs):
    argsdict = {}
    if args:
        args_name = inspect.getargspec(function)[0]
        argsdict.update(dict(itertools.izip(args_name, args)))
    if kwargs:
        argsdict.update(kwargs)
    for key in argsdict.viewkeys():
        value = argsdict[key]
        if value is None:
            argsdict[key] = ''
        elif isinstance(value, type('')):
            pass
        elif isinstance(value, type(u'')):
            argsdict[key] = value.encode('utf-8')
        elif isinstance(value, ndb.Model):
            if value.key is not None:
                argsdict[key] = str(value.key.id())
            else:
                argsdict[key] = ''
        else:
            argsdict[key] = str(argsdict[key])
    return argsdict


def cache(name=None, group=None):
    def _cache(function):
        def wrapper(*args, **kwargs):
            argsdict = _parsefunction(function, args, kwargs)
            key = _getkey(group, name, function.__name__, argsdict)
            value = memcache.get(key)
            if value is not None:
                return value
            else:
                value = function(*args, **kwargs)
                memcache.set(key, value=value, time=3600 * 24 * 5)
                return value

        return wrapper

    return _cache


def evictgroup(group):
    """evict all group's cache"""

    def _evictgroup(function):
        def wrapper(*args, **kwargs):
            value = function(*args, **kwargs)
            Group.increase(group)
            return value

        return wrapper

    return _evictgroup


def evict(name, group=""):
    """evict specify cache"""
    def _evict(function):
        def wrapper(*args, **kwargs):
            argsdict = _parsefunction(function, args, kwargs)
            key = _getkey(group, name, function.__name__, argsdict)
            value = function(*args, **kwargs)
            memcache.delete(key)
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