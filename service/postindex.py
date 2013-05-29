#coding=utf-8
__author__ = 'dongliu'

from google.appengine.api import search
from datetime import timedelta
from tools.decorators import *
import StringIO


def addpost(post):
    content = post.content
    document = search.Document(
        doc_id=str(post.key.id()),
        language='zh',
        fields=[search.TextField(name='title', value=post.title),
                search.TextField(name='tags', value=' '.join(post.tags)),
                search.HtmlField(name='content', value=content),
                search.AtomField(name='author', value=post.author.nickname()),
                search.DateField(name='published', value=post.date)])
    search.Index(name="article_index").put(document)


def delpost(postid):
    doc_index = search.Index(name="article_index")
    doc_index.delete(str(postid))


def _useem(content):
    if not content:
        return content
    return content.replace('b>', 'em>')


_ch_set = {u',', u'=', u'<', u'>', u'&', u'%', u'$', u'#', u'@', u'!', u'+', u'-', u'*', u'.', u'"', u"'", u'/', u'?',
           u':', u';', u'!', u'~', u'(', u')', u'[', u']', u'{', u'}', u'，', u'：', '；', '？', '！', u'（', u'）'}


def _escape(query):
    if not query:
        return query
    isunicode = False
    if type(query) == type(u''):
        isunicode = True
    if not isunicode:
        query = query.decode('utf-8')

    buf = StringIO.StringIO()
    for ch in query:
        if ch in _ch_set:
            buf.write(' ')
        else:
            buf.write(ch.encode('utf-8'))
    if isunicode:
        return buf.getvalue().decode('utf-8')
    return buf.getvalue()


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
        returned_fields=["author", "tags", "title", "published"],
        snippeted_fields=["title", "content"],
    )

    query = search.Query(query_string=_escape(querystr), options=options)
    index = search.Index(name="article_index")
    results = index.search(query)
    searchlist = []
    for doc in results:
        postid = int(doc.doc_id)
        tags = doc["tags"][0].value.split(' ')
        date = doc["published"][0].value
        author = doc["author"][0].value
        title = ''
        content = ''
        for expr in doc.expressions:
            if expr.name == "content":
                content = expr.value
            elif expr.name == "title":
                title = expr.value
        searchlist.append({
            'postid': postid,
            "tags": tags,
            'content': _useem(content),
            'title': _useem(title),
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
        'size': len(searchlist),
        'total': total,
        'cursor': next_cursor_urlsafe,
        'list': searchlist,
    }

@cache(group="post", name="similars-${postid}")
def getsimilars(postid, title, tags):
    """
    use title ,tags to query similar posts.
    """
    queryitems = [tag for tag in tags if tag]
    queryitems.append(title)
    querystr = ' OR '.join(queryitems)
    expr = search.SortExpression(
        expression="_score * 1.0",
        direction=search.SortExpression.DESCENDING,
        default_value=0.0)

    # Sort up to 1000 matching results by subject in descending order
    sort = search.SortOptions(expressions=[expr], limit=1000)

    options = search.QueryOptions(
        limit=5,  # the number of results to return
        sort_options=sort,
        returned_fields=["author", "tags", "title", "published", "content"],
    )

    query = search.Query(query_string=_escape(querystr), options=options)
    index = search.Index(name="article_index")
    results = index.search(query)
    search_list = []
    for doc in results:
        postid = int(doc.doc_id)
        title = doc["title"][0].value
        tags = doc["tags"][0].value.split(' ')
        date = doc["published"][0].value
        author = doc["author"][0].value
        search_list.append({
            'postid': postid,
            "tags": tags,
            'title': title,
            'author': author,
            'date': (date + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'),
            })

    return search_list