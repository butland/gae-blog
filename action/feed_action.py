#encoding=utf-8

import webapp2
from db.postdb import *
from db.configdb import *
from tools import PyRSS2Gen


class Feed(webapp2.RequestHandler):
    def get(self, tag=None):
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
            title += " - " + tag.decode('utf-8')
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
        self.response.headers["Content-Type"] = "application/rss+xml;charset=utf-8"
        rss.write_xml(self.response.out, "utf-8")