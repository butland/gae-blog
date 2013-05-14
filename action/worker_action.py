#encoding=utf-8

import webapp2
from db.post_db import Post
from db.comment_db import Comment
from google.appengine.api import mail
from google.appengine.api import app_identity
from db.config_db import *


class CommentWorker(webapp2.RequestHandler):
    # when adding a new comment ,send mail notify to post's author.
    def get(self, postid, commentid):
        self.post()

    def post(self):
        postid = int(self.request.get('postid'))
        commentid = int(self.request.get('commentid'))

        post = Post.getpost(postid)
        comment = Comment.get_by_id(commentid)
        if post is None or comment is None:
            return

        appid = app_identity.get_application_id()
        idx = appid.find('~')
        if idx > 0:
            appid = appid[0:idx]
        sender = "robot@%s.appspotmail.com" % appid

        body = u"""%s 对<a href="%s" target="_blank"/>「%s」</a>发表了评论: <br /> <br />
                %s""" % (comment.username,
                         "http://" + Config()["host"],
                         post.title,
                         comment.content)

        message = mail.EmailMessage(sender=sender, subject=u"你发表的文章有了新的评论")
        message.to = post.author.email()
        message.html = body
        message.send()