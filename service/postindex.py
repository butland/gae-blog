#coding=utf-8
__author__ = 'dongliu'

from google.appengine.api import search
from datetime import timedelta
import re
from tools.web_tools import subStr


def addpost(post):
    content = post.content
    document = search.Document(
        doc_id=str(post.key.id()),
        language='zh',
        fields=[search.TextField(name='title', value=post.title),
                search.HtmlField(name='content', value=content),
                search.AtomField(name='author', value=post.author.nickname()),
                search.DateField(name='published', value=post.date)])
    search.Index(name="article_index").put(document)


def delpost(postid):
    doc_index = search.Index(name="article_index")
    doc_index.delete(str(postid))


def _processkeys(content, keys):
    for key in keys:
        key_pattern = re.compile(re.escape(key), re.I)
        content = key_pattern.sub(lambda x: '<em>%s</em>' % x.group(), content)
    return content


def _snippet(content, keys):
    """work around for snippedted content"""
    content_size = 100 * 2
    start = 0
    length = 0
    content = content.strip()
    pattern = re.compile(r'<[^<>]+>')
    content = pattern.sub('', content)
    content_up = content.upper()
    for key in keys:
        idx = content_up.find(key.upper())
        if idx > 0:
            if len(key) > length:
                start = idx
                length = len(key)
    if start > 20:
        start -= 20
    content = content[start:]
    content = subStr(content, content_size)
    return _processkeys(content, keys)


def query(querystr, cursorstr, limit):
    expr = search.SortExpression(
        expression="_score * 1.0",
        direction=search.SortExpression.DESCENDING,
        default_value=0.0)

    # Sort up to 1000 matching results by subject in descending order
    sort = search.SortOptions(expressions=[expr], limit=1000)

    cursor = search.Cursor(web_safe_string=cursorstr)
    options = search.QueryOptions(
        limit=limit,  # the number of results to return
        cursor=cursor,
        sort_options=sort,
        returned_fields=["author", "title", "published", "content"],
        #TODO bugs on google app engine server
#            snippeted_fields=["content"],
    )

    query = search.Query(query_string=querystr, options=options)
    index = search.Index(name="article_index")
    results = index.search(query)
    list = []
    keys = [key for key in querystr.split(' ') if len(key) > 0]
    for doc in results:
        postid = int(doc.doc_id)
        content = doc["content"][0].value
        title = doc["title"][0].value
        date = doc["published"][0].value
        author = doc["author"][0].value
        list.append({
            'postid': postid,
            'content': _snippet(content, keys),
            'title': _processkeys(title, keys),
            'author': author,
            'date': (date + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'),
        })

    next_cursor = results.cursor
    if next_cursor:
        next_cursor_urlsafe = next_cursor.web_safe_string
    else:
        next_cursor_urlsafe = ''
    total = results.number_found

    return {
        'query': querystr,
        'size': len(list),
        'total': total,
        'cursor': next_cursor_urlsafe,
        'list': list,
    }

