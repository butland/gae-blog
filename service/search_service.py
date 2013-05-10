#coding=utf-8
__author__ = 'dongliu'

from google.appengine.api import search
from datetime import timedelta


class SearchService(object):

    @staticmethod
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

    @staticmethod
    def delpost(postid):
        doc_index = search.Index(name="article_index")
        doc_index.delete(str(postid))

    @staticmethod
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
        for doc in results:
            postid = int(doc.doc_id)
            content = doc["content"][0].value
            title = doc["title"][0].value
            date = doc["published"][0].value
            author = doc["author"][0].value
            list.append({
                'postid': postid,
                'content': content,
                'title': title,
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

