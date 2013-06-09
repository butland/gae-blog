#encoding=utf-8

import logging
import webapp2
from db.postdb import Post
from db.commentdb import Comment
from google.appengine.api import mail
from google.appengine.api import app_identity
from db.configdb import *
from google.appengine.api import users
from service import postindex
from db.postdb import PRIVILEGE_SHOW


class CommentWorker(webapp2.RequestHandler):
    # when adding a new comment ,send mail notify to post's author.
    def get(self):
        self.post()

    def post(self):
        postid = int(self.request.get('postid'))
        commentid = int(self.request.get('commentid'))
        replyto = self.request.get('replyto')

        post = Post.getpost(postid)
        comment = Comment.get_by_id(commentid)
        if post is None or comment is None:
            return

        appid = app_identity.get_application_id()
        idx = appid.find('~')
        if idx > 0:
            appid = appid[0:idx]
        sender = "robot@%s.appspotmail.com" % appid

        if replyto:
            pcomment = Comment.getcomment(int(replyto))
            if pcomment.email:
                body = u"""%s 回复了你对 <a href="%s" target="_blank"/>「%s」</a>发表的评论: <br /> <br />
                    %s<br /> < hr/> %s""" \
                       % (comment.username, "http://" + Config()["host"], post.title, pcomment.content, comment.content)
                try:
                    message = mail.EmailMessage(sender=sender, subject=u"你的评论有了新回复")
                    message.to = pcomment.email
                    message.html = body
                    message.send()
                except Exception as e:
                    logging.error("Send email to %s failed: %s" % (pcomment.email, str(e)))

        body = u"""%s 对<a href="%s" target="_blank"/>「%s」</a>发表了评论: <br /> <br />
                %s""" % (comment.username,
                         "http://" + Config()["host"],
                         post.title,
                         comment.content)

        try:
            message = mail.EmailMessage(sender=sender, subject=u"你发表的文章有了新的评论")
            message.to = post.author.email()
            message.html = body
            message.send()
        except Exception as e:
            logging.error("Send email to %s failed: %s" % (post.author.email(), str(e)))


class ArticleWorker(webapp2.RequestHandler):
    # when add/update/delete article ,update index.
    def get(self):
        self.post()

    def post(self):
        postid = int(self.request.get('postid'))
        post = Post.getpost(postid)
        try:
            if  post is not None and post.privilege == PRIVILEGE_SHOW:
                postindex.addpost(post)
            else:
                postindex.delpost(postid)
        except Exception as e:
            logging.error('Error when update post index: ' + str(e))