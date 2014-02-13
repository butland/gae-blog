#encoding=utf-8

from google.appengine.api import users

from service.fortune import *
from flask import (Response, request, abort)
from web import app
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name


@app.route('/tools/fortune', methods=['GET', 'POST'])
def fortune():
    return Response(rand_fortune(), mimetype='text/plain')


@app.route('/tools/highlight', methods=['GET', 'POST'])
def highlight_code():
    if not users.is_current_user_admin():
        return
    language = request.values.get('language', None)
    code = request.values.get('code', None)
    if not language or not code:
        abort(400)
    lexer = get_lexer_by_name(language, stripall=True)
    return Response(highlight(code, lexer, HtmlFormatter()), mimetype='text/html')