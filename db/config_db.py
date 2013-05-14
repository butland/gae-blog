__author__ = 'dongliu'

from google.appengine.ext import ndb
from google.appengine.api import app_identity
from tools.decorators import singleton


class Configure(ndb.Model):
    value = ndb.StringProperty(indexed=False)


def setdict(pdict, name ,value):
    ovalue = pdict[name]
    if type(ovalue) == type(1):
        pdict[name] = int(value)
    elif type(ovalue) == type(u''):
        pdict[name] = value
    elif type(ovalue) == type(''):
        pdict[name] = value
    elif type(ovalue) == type(False):
        pdict[name] = value.lower() == "true" or value.lower() == "on"

@singleton
class Config(object):
    def __init__(self):
        self._configs = {
            "heading": "Heading",
            "subheading": "subheading",
            "host": app_identity.get_default_version_hostname(),
            "abstract": False,
            "postnumperpage": 10,
            "commentnumperpage": 10,
            "feednum": 10,
            "recentcommentnum": 10,
            "recentpostnum": 10,
            "blobEnable": False,

            "picasaalbumname": "",
            "gauid": "",
            }
        for key in self._configs:
            configure = Configure.get_by_id(key)
            if configure:
                setdict(self._configs, key, configure.value)
            else:
                configure = Configure(id=key)
                configure.value = str(self._configs[key])
                configure.put()

    def __getitem__(self, item):
        return self._configs[item]

    def __setitem__(self, name, value):
        if name is None or value is None:
            return
        setdict(self._configs, name, value)
        configure = Configure(id=name)
        configure.value = value
        configure.put()

    def keys(self):
        return self._configs.keys()