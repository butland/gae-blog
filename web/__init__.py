__author__ = 'dongliu'
from flask import Flask

app = Flask(__name__)
app.debug = False

import web.webtools
import web.tools_view
import web.post_view
import web.search_view
import web.picasa_view
import web.admin_view
import web.captcha_view
import web.user_view
import web.comment_view
import web.worker_view
import web.file_view