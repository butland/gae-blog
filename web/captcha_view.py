#encoding=utf-8
__author__ = 'dongliu'

import StringIO

from google.appengine.api import memcache

from tools import captcha
from flask import (send_file, request, jsonify)
from web import app


@app.route('/captcha', methods=['GET'])
def show_captcha():
    seq = request.args.get('seq')
    mstream = StringIO.StringIO()
    code_img, code = captcha.create_validate_code()
    memcache.add(key="captcha#" + seq, value=code, time=1800)
    code_img.save(mstream, "GIF")
    mstream.seek(0)
    return send_file(mstream, mimetype='image/gif')


@app.route('/captcha/check', methods=['POST'])
def check_captcha():
    seq = request.values.get('seq')
    code = request.values.get('code')
    if not seq or not code:
        return jsonify({"state": -1})
    ocode = memcache.get("captcha#" + seq)
    if not ocode or code.strip().upper() != ocode:
        return jsonify({"state": 1})
    return jsonify({"state": 0})