#encoding=utf-8

from google.appengine.ext import ndb
from datetime import datetime, timedelta
from tools.decorators import *
from tools import text_util
import re

# deleted
PRIVILEGE_DEL = -1
# hide post
PRIVILEGE_HIDE = 0
# normal post
PRIVILEGE_SHOW = 1
# pinned post
PRIVILEGE_SPIN = 2


class Post(ndb.Model):
    title = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=False)
    author = ndb.UserProperty(indexed=False)
    content = ndb.TextProperty(indexed=False)
    privilege = ndb.IntegerProperty()
    last_modify_date = ndb.DateTimeProperty(auto_now_add=False)
    last_modify_by = ndb.UserProperty(indexed=False)
    tags = ndb.StringProperty(repeated=True)
    commentCount = ndb.IntegerProperty()

    @staticmethod
    @cache(group="post", name="${privilege}-${offset}-${limit}-${tag}-${archive}")
    def _get_postid_list(privilege, offset, limit, tag=None, archive=None):
        q = Post.query()
        q = q.filter(Post.privilege == privilege)
        if tag:
            q = q.filter(Post.tags == tag)
        if archive:
            start_date = datetime.strptime(archive, '%Y-%m') - timedelta(hours=8)
            year, month = (int(item) for item in archive.split('-'))
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
            end_date = datetime.strptime('%d-%d' % (year, month), '%Y-%m') - timedelta(hours=8)
            q = q.filter(Post.date >= start_date)
            q = q.filter(Post.date < end_date)
        q = q.order(-Post.date)
        return q.fetch(offset=offset, limit=limit, keys_only=True)

    @staticmethod
    def get_postlist(privilege, offset, limit, tag=None, archive=None):
        post_list = []
        for postkey in Post._get_postid_list(privilege, offset, limit, tag, archive):
            post = Post.getpost(postkey.id())
            if post is None:
                post.key = postkey
                post.title = 'not Found'
            post_list.append(post)
        return post_list

    @staticmethod
    @cache(group="post", name="count-${privilege}")
    def count(privilege):
        q = Post.query()
        q = q.filter(Post.privilege == privilege)
        return q.count(limit=99999)

    @staticmethod
    @cache(name="post-${postid}")
    def getpost(postid):
        try:
            return Post.get_by_id(postid)
        except:
            return None

    @staticmethod
    @evictgroup("post")
    @evict(name="post-${post}")
    def savepost(post):
        return post.put()

    def abstract(self, length=400):
        """
        return abstract of content.
        It is implemented by simple way now.
        """
        content = self.content
        content = re.sub(r'<[^<>]+>', '', content)
        content = text_util.subStr(content, length * 2)
        return content