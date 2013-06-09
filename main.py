#encoding=utf-8

from google.appengine.ext.webapp.util import run_wsgi_app
from web import app

run_wsgi_app(app)