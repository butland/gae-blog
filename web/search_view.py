#encoding=utf-8
__author__ = 'dongliu'

from service import postindex
from flask import (render_template, request, jsonify)
from web import app
from db.configdb import Config

@app.route('/search', methods=['GET'])
def search_page():
    return render_template('search.html', query=request.args.get('query'), config=Config())


@app.route('/search/ajax', methods=['GET'])
def search_api():
    query = request.args.get('query')
    cursor = request.args.get('cursor')
    pagesize = int(request.args.get('pagesize'))
    result = postindex.query(query, cursor, pagesize)
    return jsonify(result)