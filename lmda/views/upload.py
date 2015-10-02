import json
import os
import random
import string
from flask import render_template, request
from flask.ext.login import current_user
from lmda import app, database


class UploadResponse:
    def __init__(self):
        self.errors = []


class ResponseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)
        values = obj.__dict__
        return values


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/api/upload', methods=['PUT'])
def put_upload():
    response = UploadResponse()
    file = request.files['file']
    if file:
        extension_split = file.filename.split('.')
        if len(extension_split) < 1:
            response.errors.append('File is missing extension. Name was ' + file.filename + '.')
            return json.dumps(response, cls=ResponseEncoder), 400

        extension = extension_split[-1]
        extension_allowed = extension in app.config['ALLOWED_TYPES']
        if not extension_allowed:
            response.errors.append('Extension not allowed: ' + extension)

        filename = gen_filename()
        if filename is None:
            response.errors.append('Error generating filename')
            return json.dumps(response, cls=ResponseEncoder), 500

        try:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + '.' + extension))
            response.url = filename

            from lmda.models import File, User
            if current_user.is_anonymous():
                cur_uid = -1
            else:
                cur_uid = current_user.id
            file = File(owner=cur_uid, name=filename, extension=extension, encrypted=False, local_name=file.filename)
            database.session.add(file)
            database.session.commit()

            # SUCCESS !!!

            return json.dumps(response, cls=ResponseEncoder)
        except:
            response.errors.append('Error saving file')
            return json.dumps(response, cls=ResponseEncoder), 500
    else:
        response.errors.append('No file sent')
        return json.dumps(response, cls=ResponseEncoder), 400


def gen_filename(max_tries=5, start_length=3, tries_per_len_incr=3):
    # TODO check pastes

    tries = 0
    while True:
        if tries >= max_tries:
            return None

        extra_length = int(tries/tries_per_len_incr)

        filename = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(start_length + extra_length))
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.isfile(path):  # file exists
            tries += 1
            continue

        for extension in app.config['ALLOWED_TYPES']:
            if os.path.isfile(path + '.' + extension):  # file exists
                tries += 1
                continue

        return filename
