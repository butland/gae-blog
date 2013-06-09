__author__ = 'dongliu'

import jinja2
import os
import urllib
from google.appengine.api import users
from db.postdb import *
from db.configdb import *
from db.tagdb import *
from db.commentdb import *
from datetime import datetime, timedelta
from web import app


def subStr(str, length):
    #str must be unicode
    if str is None:
        return None
    if len(str) * 2 < length:
        return str
    pos = -1
    curlen = 0
    low = 0x4E00
    high = 0x9FA5
    for ch in str:
        if low <= ord(ch) <= high:
            curlen += 2
        else:
            curlen += 1
        pos += 1
        if curlen > length:
            break
    if pos >= len(str):
        return str
    if pos > 2:
        pos -= 2
    return str[0:pos] + '...'


# url encode fuc for jinja
def urlEncode(text):
    return urllib.quote(text.encode('utf-8'))

@app.template_filter('tag')
def encodetag(tag):
    if not tag:
        return tag
    return urllib.quote(tag.encode('utf-8')).replace('/', '%252F')


def get_spin_posts():
    return Post.get_postlist(PRIVILEGE_SPIN, 0, 5)


def get_recent_posts():
    return Post.get_postlist(PRIVILEGE_SHOW, 0, Config()["recentpostnum"])


def get_archives():
    archives = Tag.get_taglist(CID_ARCHIVE)
    archives.sort(key=lambda a: a.name, reverse=True)
    return archives


def get_alltags():
    return Tag.get_taglist(CID_TAG)


def get_recent_comments():
    comment_list = Comment.get_commentlist(0, Config()["recentcommentnum"])
    for comment in comment_list:
        comment.content = subStr(comment.content, 33*2)
    return comment_list


def get_fortune():
    from service import fortune
    return fortune.rand_fortune().decode('utf-8')


def get_post_title(postid):
    return Post.getpost(postid).title;


@app.template_filter('datetime')
def format_datetime(date):
    if date is None:
        return ''
    date = date + timedelta(hours=8)
    return date.strftime('%Y-%m-%d %H:%M')

@app.template_filter('datetimelocal')
def format_datetime_local(date):
    """used with html5 datetime-local input type"""
    if date is None:
        return ''
    date = date + timedelta(hours=8)
    return date.strftime('%Y-%m-%dT%H:%M')

@app.template_filter('before')
def substring_before(str, dem):
    idx = str.find(dem)
    if idx < 0:
        return str
    return str[0:idx]

# for jinja functions
app.jinja_env.globals.update({
    'getuser': users.get_current_user,
    'isadmin': users.is_current_user_admin,

    'get_spin_posts': get_spin_posts,
    'get_recent_posts': get_recent_posts,
    'get_recent_comments': get_recent_comments,
    'get_alltags': get_alltags,
    'get_archives': get_archives,
    'get_fortune': get_fortune,
    'get_post_title': get_post_title,
    'encode': urlEncode,
})