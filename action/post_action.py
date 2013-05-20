#encoding=utf-8

import webapp2
from db.config_db import *
from db.post_db import *
from db.tag_db import *
from db.comment_db import *
from tools.pager_tool import *
from tools.web_tools import *
from tools import pinyin
from datetime import datetime,timedelta,time
from google.appengine.api import users
from service import postindex
import random


def emptyPost():
    post = Post()
    post.title = ''
    post.content = ''
    post.date = datetime.today()
    post.tags = []
    post.privilege = 1
    post.commentCount = 0
    post.last_modify_date = datetime.today()
    return post


def is_post_public(post):
    return post is not None and post.privilege == PRIVILEGE_SHOW


def on_post_change(opost, post):
    """
    deal with tags, counts, and index when post have been changed.
    """
    if is_post_public(opost):
        if is_post_public(post):
            postindex.addpost(post)
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
            postindex.delpost(opost.key.id())
            Tag.decrease(CID_COUNTER, NAME_ALLPOST)
            Tag.decrease(CID_ARCHIVE, (opost.date+timedelta(hours=8)).strftime('%Y-%m'))
            for tag in opost.tags:
                if tag:
                    Tag.decrease(CID_TAG, tag)

    else:
        if is_post_public(post):
            postindex.addpost(post)
            Tag.increase(CID_COUNTER, NAME_ALLPOST)
            Tag.increase(CID_ARCHIVE, (post.date+timedelta(hours=8)).strftime('%Y-%m'))
            for tag in post.tags:
                if tag:
                    Tag.increase(CID_TAG, tag)
        else:
            pass


class PostList(webapp2.RequestHandler):
    """
    show post list
    """
    def get(self, pagenum='1', tag=None, archive=None):
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
            base = '/post/list/' + encodetag(tag.decode('utf-8')) + '/'
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
        if tag:
            tag = tag.decode('utf-8')
        template_values = {
            'postlist': postlist,
            'pager': pager,
            'tag': tag,
            'archive': archive,
        }
        show_html(self.response, 'post_list.html', template_values)


class PostDetail(webapp2.RequestHandler):
    """
    show detail post.
    """
    def get(self, postidStr):
        postid = int(postidStr)
        post = Post.getpost(postid)
        if post is None:
            self.response.error(404)
            return
        if post.privilege <= 0 and not users.is_current_user_admin():
            self.response.error(404)
            return
        seq = "%s%s" % (time(), random.randint(10000, 99999))
        template_values = {
            "post": post,
            "seq": seq,
        }
        show_html(self.response, 'post_view.html', template_values)


class PostEdit(webapp2.RequestHandler):
    """
    show post new/edit page.
    """
    def get(self):
        if not users.is_current_user_admin():
            return
        postidstr = self.request.get('postid')
        # edit
        if postidstr:
            postid = int(postidstr)
            post = Post.getpost(postid)
        else:
            # new
            post = emptyPost()
        alltags = Tag.get_taglist(CID_TAG)
        taglist = [{"name":tag.name, "spell":pinyin.getpinyin(tag.name)} for tag in alltags if tag]
        template_values = {
            "post": post,
            "taglist": taglist,
        }
        show_html(self.response, 'post_edit.html', template_values)


class PostUpdate(webapp2.RequestHandler):
    """
    add or update post
    """
    def post(self):
        if not users.is_current_user_admin():
            return
        postidstr = self.request.get('postid')
        if not postidstr:
            postid = 0
        else:
            postid = int(postidstr)
        if postid != 0:
            post = Post.getpost(postid)
            opost = Post()
            opost.privilege = post.privilege
            opost.tags = post.tags
            opost.date = post.date
            post.last_modify_date = datetime.today()
            post.last_modify_by = users.get_current_user()
        else:
            post = emptyPost()
            opost = None
            post.author = users.get_current_user()
        post.title = self.request.get('title')
        post.content = self.request.get('content')
        post.tags = [ tag for tag in self.request.POST.getall('tags') if tag ]
        post.privilege = int(self.request.get('privilege'))
        post.date = datetime.strptime(self.request.get('pubdate'), '%Y-%m-%dT%H:%M:%S') - timedelta(hours=8)
        newid = Post.savepost(post)
        on_post_change(opost, post)
        self.redirect('/post/' + str(newid.id()))


class PostDelete(webapp2.RequestHandler):
    """
    delete post.
    """
    def get(self):
        if not users.is_current_user_admin():
            return
        postidstr = self.request.get('postid')
        if not postidstr:
            return
        post = Post.getpost(int(postidstr))
        if post:
            on_post_change(post, None)
            post.privilege = PRIVILEGE_DEL
            post.commentCount = 0
            Post.savepost(post)
            Comment.delete_comment_bypost(post.key.id())
        self.redirect('/')
