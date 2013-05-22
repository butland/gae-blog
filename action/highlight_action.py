#encoding=utf-8

import webapp2
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from google.appengine.api import users



class Highlighter(webapp2.RequestHandler):
    """output highlight code use pygments"""

    def post(self):
        if not users.is_current_user_admin():
            return
        language = self.request.get('language')
        code = self.request.get('code')
        if not language or not code:
            return None
        lexer = get_lexer_by_name(language, stripall=True)
        self.response.headers["Content-Type"] = "text/html;charset=utf-8"
        self.response.out.write(highlight(code, lexer, HtmlFormatter()))