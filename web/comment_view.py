#coding=utf-8
__author__ = 'dongliu'

import StringIO
import cgi
import webapp2
from db.postdb import *
from db.commentdb import *
from db.configdb import Config
from datetime import datetime,timedelta
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.api import taskqueue
import json
from flask import (render_template, request, jsonify, abort)
from web import app

@app.route('/comment/<int:postid>/<int:page>', methods=['GET'])
def comment_list(postid, page):
    post = Post.getpost(postid)
    count = post.commentCount
    if count is None:
        count = 0
    cpagesize = Config()["commentnumperpage"]
    commentlist = Comment.get_commentlist_bypost(postid, (page - 1) * cpagesize, cpagesize)

    isadmin = users.is_current_user_admin()
    result = {
        "count": count,
        "page": page,
        "pagecount": (count - 1) / cpagesize + 1,
        "clist": [comment.to_dict(isadmin) for comment in commentlist]
    }
    return jsonify(result)


def _escapehtml(string):
    if not string:
        return string
    buf = StringIO.StringIO()
    for ch in string:
        if ch != '<' and ch != '>' and ch != '&' and ch != '"' and ch != "'":
            buf.write(ch)
    return buf.getvalue()


@app.route('/comment/add', methods=['POST'])
def add_comment():
    postid = int(request.values.get('postid'))
    user = users.get_current_user()
    if not user:
        # check captcha
        captcha = request.values.get('code')
        seq = request.values.get('seq')
        code = memcache.get("captcha#" + seq)
        memcache.delete("captcha#" + seq)
        if captcha is None or captcha.strip().upper() != code:
            return jsonify({'state': 1, 'msg': u'验证码错误'})

    comment = Comment()

    post = Post.getpost(postid)
    if post is None:
        return jsonify({'state': -1, 'msg': u'不存在的文章'})

    comment.postId = postid
    comment.content = request.values.get('content')
    comment.username = request.values.get('username')
    comment.email = _escapehtml(request.values.get('email'))
    comment.homepage = _escapehtml(request.values.get('homepage'))
    comment.ip = request.remote_addr
    comment.date = datetime.today()

    replyto = request.values.get('replyto')
    if replyto:
        pcomment = Comment.getcomment(int(replyto))
        pcomment = pcomment.to_pdict()
        if pcomment:
            comment.parentContent = json.dumps(pcomment)
    if not comment.email:
        comment.email = "default@default.com"
    if comment.homepage and not comment.homepage.startswith('http'):
        comment.homepage = 'http://' + comment.homepage

    commentid = Comment.savecomment(comment)

    if post.commentCount is None:
        post.commentCount = 0
    post.commentCount += 1
    Post.savepost(post)

    # notify the woker
    taskqueue.add(
        url='/worker/comment',
        params={'postid': str(postid), 'replyto': replyto, 'commentid': str(commentid.id())})

    return jsonify({'state': 0, 'msg': ''})


@app.route('/comment/delete', methods=['POST'])
def delete_comment():
    if not users.is_current_user_admin():
        abort(403)
    commentid = int(request.values.get('commentid'))
    comment = Comment.getcomment(commentid)
    postid = comment.postId
    Comment.deletecomment(comment)
    post = Post.getpost(postid)
    if post.commentCount is None:
        post.commentCount = 0
    post.commentCount -= 1
    if post.commentCount < 0:
        post.commentCount = 0
    Post.savepost(post)
    return jsonify({'state': 0})