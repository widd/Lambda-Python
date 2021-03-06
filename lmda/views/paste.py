import datetime
import json
from flask import render_template, request, Response, abort
from flask_login import current_user
from lmda import app, ResponseEncoder, db
from lmda.models import Paste
from lmda.views.upload import gen_filename


class EmptyClass:
    pass


@app.route('/paste', methods=['GET'])
def paste():
    return render_template('paste.html')


@app.route('/api/paste', methods=['GET'])
def get_paste():
    response = EmptyClass()
    response.errors = []

    name = request.args.get('name')
    if name is None:
        response.errors.append("No name sent")
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

    paste = Paste.by_name(name)
    if paste is not None:
        return Response(paste.content_json, mimetype='application/json')
    else:
        response.errors.append("No paste with name")
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')


@app.route('/api/paste', methods=['POST'])
def put_paste():
    response = EmptyClass()
    response.errors = []

    api_key = request.form.get('api_key')
    paste_text = request.form.get('paste')
    is_code = request.form.get('is_code', False)

    if paste_text is None:
        response.errors.append("No paste data sent")
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

    user = current_user

    if user.is_anonymous and api_key is not None:
        from lmda.models import User
        user = User.by_api_key(api_key)

    if user is not None and not user.is_anonymous:
        uploader_id = user.id
    else:
        uploader_id = -1

    filename = gen_filename()

    paste = Paste(name=filename, owner=uploader_id, content_json=paste_text, is_code=is_code, upload_date=datetime.datetime.utcnow())
    db.session.add(paste)
    db.session.commit()

    response.url = filename
    return Response(json.dumps(response, cls=ResponseEncoder), mimetype='application/json')


def view_paste(name):
    paste = Paste.by_name(name)
    if paste is not None:
        return render_template('viewPaste.html')
    abort(404)
