#encoding=utf-8
import os
import webapp2
from action.post_action import *
from action.captcha_action import *
from action.user_action import *
from action.comment_action import *
from action.fortune_action import *
from action.picasa_action import *
from action.search_action import *
from action.feed_action import *
from action.file_action import *
from action.admin_action import *
from action.worker_action import *

app = webapp2.WSGIApplication([('/', PostList), ('/post', PostList),
                            webapp2.Route('/post/list/<pagenum:\d+>', handler=PostList, name='post-list'),
                            webapp2.Route('/post/list/<tag>/', handler=PostList, name='post-list'),
                            webapp2.Route('/post/list/<tag>/<pagenum:\d+>', handler=PostList, name='post-list'),
                            webapp2.Route('/post/archive/<archive:[\d-]+>/', handler=PostList, name='post-list'),
                            webapp2.Route('/post/archive/<archive:[\d-]+>/<pagenum:\d+>', handler=PostList, name='post-list'),
                            ('/post/(\d+)', PostDetail),
                            ('/post/edit', PostEdit),
                            ('/post/update', PostUpdate),
                            ('/post/delete', PostDelete),
                            ('/comment/(\d+)/(\d+)', CommentList),
                            ('/comment/add', CommentInsert),
                            ('/comment/delete', CommentDelete),
                            ('/album', PicasaList),
                            ('/album/([^/]+)/', PicasaAlbum),
                            ('/search', SearchPage),
                            ('/search/ajax', SearchAjax),
                            ('/feed', Feed),
                            ('/feed/([^/]+)', Feed),
                            ('/captcha', Captcha),
                            ('/captcha/check', CaptchaCheck),
                            ('/showimage/(\d+)', FileShow),
                            ('/showfile/(\d+)', FileShow),
                            ('/file/upload', FileUpload),
                            ('/file/delete', FileDelete),
                            ('/blob/show/([^/]+)', BlobShow),
                            ('/tools/fortune', Fortune),
                            ('/admin/config', AdminConfig),
                            ('/admin/file', AdminFile),
                            ('/worker/comment', CommentWorker),
                            ('/login', Login),
                            ('/logout', Logout),
                            ],debug=True)