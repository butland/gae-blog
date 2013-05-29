#encoding=utf-8

from google.appengine.ext import ndb
from tools.decorators import *


class Comment(ndb.Model):
    postId = ndb.IntegerProperty()
    date = ndb.DateTimeProperty()
    author = ndb.UserProperty(indexed=False)
    content = ndb.TextProperty(indexed=False)
    parentContent = ndb.TextProperty(indexed=False)
    username = ndb.StringProperty(indexed=False)
    homepage = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    ip = ndb.StringProperty(indexed=False)

    @staticmethod
    @cache(group="comment", name="${offset}-${limit}")
    def get_commentlist(offset, limit):
        q = Comment.query()
        q = q.order(-Comment.date)
        return q.fetch(offset=offset, limit=limit)

    @staticmethod
    @cache(group="comment", name="${postid}-${offset}-${limit}")
    def get_commentlist_bypost(postid, offset, limit):
        q = Comment.query()
        q = q.filter(Comment.postId == postid)
        q = q.order(-Comment.date)
        return q.fetch(offset=offset, limit=limit)

    @staticmethod
    @evictgroup("comment")
    def delete_comment_bypost(postid):
        q = Comment.query()
        q = q.filter(Comment.postId == postid)
        for m in q.fetch(keys_only=True):
            m.delete()

    @staticmethod
    @evictgroup("comment")
    def savecomment(comment):
        return comment.put()

    @staticmethod
    @evictgroup("comment")
    def deletecomment(comment):
        comment.key.delete()

    @staticmethod
    def getcomment(commentid):
        return Comment.get_by_id(commentid)

    def to_dict(self, isadmin):
        from datetime import datetime, timedelta
        import hashlib
        import json
        if self.email:
            email = self.email
        else:
            email = "default@default.com"
        output = {
            "id": self.key.id(),
            "postId": self.postId,
            "date": (self.date + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'),
            "content": self.content,
            "username": self.username,
            "homepage": self.homepage,
            "admin": isadmin,
            "avatar": "http://0.gravatar.com/avatar/" + hashlib.md5(email.encode('utf-8')).hexdigest().lower() + "?s=64"
        }
        if isadmin:
            output["email"] = self.email
            output["ip"] = self.ip
        if self.parentContent:
            pc = json.loads(self.parentContent)
            if pc.get(email):
                pc["email"] = "default@default.com"
            pc["avatar"] = "http://0.gravatar.com/avatar/" + hashlib.md5(pc["email"].encode('utf-8')).hexdigest().lower() + "?s=64"
            output["parentContent"] = pc
            if not isadmin:
                if pc.get("ip"):
                    del pc["ip"]
                if pc.get("email"):
                    del pc["email"]
        return output

    def to_pdict(self):
        from datetime import datetime, timedelta
        output = {
            "id": self.key.id(),
            "postId": self.postId,
            "date": (self.date + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'),
            "content": self.content,
            "username": self.username,
            "homepage": self.homepage,
            "email": self.email,
            "ip": self.ip,
        }
        return output