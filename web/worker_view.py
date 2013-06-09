#encoding=utf-8
__author__ = 'dongliu'


import logging
from db.postdb import Post
from db.commentdb import Comment
from google.appengine.api import mail
from google.appengine.api import app_identity
from db.configdb import *
from google.appengine.api import users
from service import postindex
from db.postdb import PRIVILEGE_SHOW
from web import app
from flask import (request, make_response)


@app.route('/worker/comment', methods=['GET', 'POST'])
def comment_worker():
    # when adding a new comment ,send mail notify to post's author.
    postid = int(request.values.get('postid'))
    commentid = int(request.values.get('commentid'))
    replyto = request.values.get('replyto')

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
    return make_response('', 200)


@app.route('/worker/article', methods=['GET', 'POST'])
def post_worker():
    # when add/update/delete article ,update index.

    postid = int(request.values.get('postid'))
    post = Post.getpost(postid)
    try:
        if  post is not None and post.privilege == PRIVILEGE_SHOW:
            postindex.addpost(post)
        else:
            postindex.delpost(postid)
    except Exception as e:
        logging.error('Error when update post index: ' + str(e))
    return make_response('', 200)
