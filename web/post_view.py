#coding=utf-8
__author__ = 'dongliu'

from db.configdb import *
from db.postdb import *
from db.tagdb import *
from db.commentdb import *
from tools.pagertool import *
from tools import (pinyin, PyRSS2Gen, platform)
from service import postindex
from db.configdb import Config
from datetime import (datetime, timedelta, time)
import random
import webtools
from google.appengine.api import (users, taskqueue)
from flask import (Response, render_template, abort, request, redirect, jsonify)
from web import app


def _emptyPost():
    post = Post()
    post.title = ''
    post.content = ''
    post.date = datetime.today()
    post.tags = []
    post.privilege = 1
    post.commentCount = 0
    post.last_modify_date = datetime.today()
    return post


def _post_public(post):
    return post is not None and post.privilege == PRIVILEGE_SHOW


def _post_change(opost, post):
    """
    deal with tags, counts, and index when post have been changed.
    """
    if _post_public(opost):
        if _post_public(post):
            oarchive = (opost.date+timedelta(hours=8)).strftime('%Y-%m')
            archive = (post.date+timedelta(hours=8)).strftime('%Y-%m')
            if oarchive != archive:
                Tag.decrease(CID_ARCHIVE, oarchive)
                Tag.increase(CID_ARCHIVE, archive)
            otags = [tag for tag in opost.tags if tag not in post.tags]
            tags = [tag for tag in post.tags if tag not in opost.tags]
            for tag in otags:
                Tag.decrease(CID_TAG, tag)
            for tag in tags:
                Tag.increase(CID_TAG, tag)
        else:
            Tag.decrease(CID_COUNTER, NAME_ALLPOST)
            Tag.decrease(CID_ARCHIVE, (opost.date+timedelta(hours=8)).strftime('%Y-%m'))
            for tag in opost.tags:
                if tag:
                    Tag.decrease(CID_TAG, tag)

    else:
        if _post_public(post):
            Tag.increase(CID_COUNTER, NAME_ALLPOST)
            Tag.increase(CID_ARCHIVE, (post.date+timedelta(hours=8)).strftime('%Y-%m'))
            for tag in post.tags:
                if tag:
                    Tag.increase(CID_TAG, tag)
        else:
            pass

@app.route('/', methods=['GET'], defaults={'tag': None, "archive": None, "pagenum": 1})
@app.route('/post', methods=['GET'], defaults={'tag': None, "archive": None, "pagenum": 1})
@app.route('/post/list/<int:pagenum>', methods=['GET'], defaults={'tag': None, "archive": None})
@app.route('/post/list/<tag>', methods=['GET'], defaults={"pagenum": 1, "archive": None})
@app.route('/post/list/<tag>/', methods=['GET'], defaults={"pagenum": 1, "archive": None})
@app.route('/post/list/<tag>/<int:pagenum>', methods=['GET'], defaults={"archive": None})
@app.route('/post/archive/<archive>', methods=['GET'], defaults={"pagenum": 1, "tag": None})
@app.route('/post/archive/<archive>/', methods=['GET'], defaults={"pagenum": 1, "tag": None})
@app.route('/post/archive/<archive>/<int:pagenum>', methods=['GET'], defaults={"tag": None})
def post_list(pagenum, tag, archive):
    """show post list"""
    try:
        page = int(pagenum)
    except Exception, ex:
        page = 1
    config = Config()
    if tag:
        tag = tag.replace('%2F', '/')
        total_tag = Tag.get_tag(CID_TAG, tag)
    elif archive:
        total_tag = Tag.get_tag(CID_ARCHIVE, archive)
    else:
        total_tag = Tag.get_tag(CID_COUNTER, NAME_ALLPOST)
    if total_tag:
        total = total_tag.count
    else:
        total = 0
    pager = Pager(total, page, config["postnumperpage"])

    if tag:
        base = '/post/list/' + webtools.encodetag(tag) + '/'
    elif archive:
        base = '/post/archive/' + archive + '/'
    else:
        base = '/post/list/'
    pager.setbase(base)

    postlist = Post.get_postlist(
        privilege=PRIVILEGE_SHOW,
        offset=pager.offset,
        limit=pager.pagesize,
        tag=tag,
        archive=archive)

    pf = platform.get_platform(request.headers.get('User-Agent'))
    if pf == platform.PHONE:
        tpl = "m/m_post_list.html"
    else:
        tpl = "post_list.html"
    return render_template(tpl, postlist=postlist, pager=pager, tag=tag, archive=archive, config=Config())

@app.route('/post/<int:postid>', methods=['GET'])
def view_post(postid):
    """ show detail post."""
    post = Post.getpost(postid)
    if post is None:
        return abort(404)
    if post.privilege <= 0 and not users.is_current_user_admin():
        return abort(404)

    # get similar posts
    # try:
    #     similars = postindex.getsimilars(postid, post.title, post.tags)
    # except Exception as e:
    #     # search api may not be enabled, or have bugs.
    #     similars = []

    pf = platform.get_platform(request.headers.get('User-Agent'))
    if pf == platform.PHONE:
        tpl = "m/m_post.html"
    else:
        tpl = "post_view.html"
    return render_template(tpl, post=post, similars=[], config=Config())


@app.route('/post/edit', methods=['GET'])
def edit_post():
    """show post new/edit page."""
    if not users.is_current_user_admin():
        return abort(403)

    postidstr = request.args.get('postid')
    if postidstr:
        # edit
        postid = int(postidstr)
        post = Post.getpost(postid)
    else:
        # new
        post = _emptyPost()
    alltags = Tag.get_taglist(CID_TAG)
    taglist = [{"name":tag.name, "spell":pinyin.getpinyin(tag.name)} for tag in alltags if tag]
    return render_template('post_edit.html', post=post, taglist=taglist, config=Config())

@app.route('/post/update', methods=['POST'])
def update_post():
    """ add or update post """
    if not users.is_current_user_admin():
        return abort(403)
    postidstr = request.values.get('postid')
    if not postidstr:
        postid = None
    else:
        postid = int(postidstr)

    if postid is not None:
        post = Post.getpost(postid)
        opost = Post()
        opost.privilege = post.privilege
        opost.tags = post.tags
        opost.date = post.date
        post.last_modify_date = datetime.today()
        post.last_modify_by = users.get_current_user()
    else:
        post = _emptyPost()
        opost = None
        post.author = users.get_current_user()
    post.title = request.values.get('title')
    post.content = request.values.get('content')
    post.tags = [ tag for tag in request.values.getlist('tags') if tag ]
    post.privilege = int(request.values.get('privilege'))
    post.date = datetime.strptime(request.values.get('pubdate'), '%Y-%m-%dT%H:%M') - timedelta(hours=8)
    newid = Post.savepost(post)
    taskqueue.add(url='/worker/article', params={'postid': str(newid.id())})
    _post_change(opost, post)
    return redirect('/post/' + str(newid.id()))


@app.route('/post/delete', methods=['POST'])
def delete_post():
    """delete a post.now it is implemented by mark the status to be PRIVILEGE_DEL."""

    if not users.is_current_user_admin():
        return abort(403)
    postidstr = request.values.get('postid')
    if not postidstr:
        return abort(404)
    post = Post.getpost(int(postidstr))
    if post:
        _post_change(post, None)
        post.privilege = PRIVILEGE_DEL
        post.commentCount = 0
        Post.savepost(post)
        Comment.delete_comment_bypost(post.key.id())
        taskqueue.add(url='/worker/article', params={'postid': postidstr})
        return jsonify({'state': 0, 'msg': ''})

    return jsonify({'state': 1, 'msg': u'此文章不存在'})


@app.route('/feed', methods=['GET'], defaults={'tag': None})
@app.route('/feed/<tag>', methods=['GET'])
@app.route('/feed/tag/<tag>', methods=['GET'])
def feed(tag):
    """rss 2.0 feed"""
    if tag:
        tag = tag.replace('%2F', '/')
    config = Config()
    postlist = Post.get_postlist(
        privilege=PRIVILEGE_SHOW,
        offset=0,
        limit=config["feednum"],
        tag=tag,
        archive=None)
    title = config["heading"]
    if tag:
        title += u" - " + tag
    link = "http://" + config["host"]
    description = config["subheading"]
    items = []
    for post in postlist:
        items.append(PyRSS2Gen.RSSItem(
            title=post.title,
            link="http://" + config["host"] + "/post/" + str(post.key.id()),
            description=post.content,
            pubDate=post.date,
            ))
    rss = PyRSS2Gen.RSS2(
        title=title,
        link=link,
        description=description,
        items=items,
        )
    return Response(rss.to_xml(), mimetype='application/rss+xml')