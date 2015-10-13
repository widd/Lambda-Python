import json
import os
import random
import string
from flask import render_template, request, Response
from flask.ext.login import current_user
import sys
from lmda import app, db, thumbnail_process_pool
from lmda.models import Thumbnail, Paste
from thumnail_create import create_thumbnail

# TODO use application/json mimetype everywhere that json is returned


class UploadResponse:
    def __init__(self):
        self.errors = []


class ResponseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)
        values = obj.__dict__
        return values


class LegacyResponseFile:
    def __init__(self, url):
        self.url = url


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/api/upload/restrictions', methods=['GET'])
def restrictions():
    response = UploadResponse()

    response.anonymous_upload = app.config["ANONYMOUS_UPLOAD"]
    response.allowed_types = app.config['ALLOWED_TYPES']
    response.max_filesize_mb = app.config['MAX_FILESIZE_MB']
    response.max_anon_filesize_mb = app.config['MAX_ANONYMOUS_FILESIZE_MB']
    response.upload_domain = app.config['UPLOAD_DOMAIN']
    response.no_extension_types = app.config['NO_EXTENSION_TYPES']

    return Response(json.dumps(response, cls=ResponseEncoder), mimetype='application/json')


@app.route('/upload', methods=['POST'])
def legacy_upload():  # LEGACY, DO NOT USE, WILL BE REMOVED SOON
    api_key = request.form.get('apikey')

    response = UploadResponse()

    if api_key is None:
        response.errors.append('No api key POSTed')

        # No 400 code is intentional because the old API gave a 200
        # Not setting json mime type is intentional because the old API didn't set it
        return json.dumps(response, cls=ResponseEncoder)

    from lmda.models import User
    user = User.by_api_key(api_key)

    if user is None:
        response.errors.append('Invalid API key')
        # No 400 code is intentional because the old API gave a 200
        # Not setting json mime type is intentional because the old API didn't set it
        return json.dumps(response, cls=ResponseEncoder)

    file = request.files['file']
    if file:
        extension_split = file.filename.split('.')
        if len(extension_split) < 1:
            response.errors.append('File is missing extension. Name was ' + file.filename + '.')
            return json.dumps(response, cls=ResponseEncoder), 400

        extension = extension_split[-1]
        extension_allowed = app.config.get('ALLOWED_TYPES', None) is None or extension in app.config['ALLOWED_TYPES']
        if not extension_allowed:
            response.errors.append('Extension not allowed: ' + extension)

        filename = gen_filename()
        if filename is None:
            response.errors.append('Error generating filename')
            return json.dumps(response, cls=ResponseEncoder), 500

        try:
            relative_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.' + extension)
            absolute_filename = os.path.abspath(relative_filename)
            file.save(relative_filename)

            response.files = [LegacyResponseFile(filename)]

            if extension not in app.config['NO_EXTENSION_TYPES']:
                response.files[0].url += '.' + extension

            if file.content_length > app.config['MAX_FILESIZE_MB']*1000000:
                response.errors.append('Filesize ' + str(file.content_length/1000000) + ' > ' + app.config['MAX_FILESIZE_MB'] + ' MB')
                # No 400 code is intentional because the old API gave a 200
                # Not setting json mime type is intentional because the old API didn't set it
                return json.dumps(response, cls=ResponseEncoder)

            # Make sure they didn't lie in content_length
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            if file_length > app.config['MAX_FILESIZE_MB']*1000000:
                response.errors.append('Filesize ' + str(file_length/1000000) + ' > ' + app.config['MAX_FILESIZE_MB'] + ' MB')
                # No 400 code is intentional because the old API gave a 200
                # Not setting json mime type is intentional because the old API didn't set it
                return json.dumps(response, cls=ResponseEncoder)

            from lmda.models import File
            file = File(owner=user.id, name=filename, extension=extension, encrypted=False, local_name=file.filename,
                        has_thumbnail=False)
            db.session.add(file)
            db.session.commit()

            # SUCCESS !!!

            # Create thumbnail
            if extension in app.config['THUMBNAIL_TYPES']:
                from lmda.models import Thumbnail
                thumbnail_process_pool.apply_async(
                    create_thumbnail,
                    args=(absolute_filename, filename),
                    callback=add_thumbnail
                )

            return json.dumps(response, cls=ResponseEncoder)
        except IOError as e:
            sys.stderr.write(str(e))
            sys.stderr.write('\n')
            response.errors.append('Error saving file')
            response.errors.append(str(e))
            # No 500 code is intentional because the old API gave a 200
            return json.dumps(response, cls=ResponseEncoder)
    else:
        response.errors.append('No file sent. Please send a file as "file".')
        # Not setting json mime type is intentional because the old API didn't set it
        return json.dumps(response, cls=ResponseEncoder)


@app.route('/api/upload', methods=['PUT'])
def put_upload():
    response = UploadResponse()
    file = request.files['file']
    if file:
        extension_split = file.filename.split('.')
        if len(extension_split) < 1:
            response.errors.append('File is missing extension. Name was ' + file.filename + '.')
            return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

        extension = extension_split[-1]
        extension_allowed = app.config.get('ALLOWED_TYPES', None) is None or extension in app.config['ALLOWED_TYPES']
        if not extension_allowed:
            response.errors.append('Extension not allowed: ' + extension)

        filename = gen_filename()
        if filename is None:
            response.errors.append('Error generating filename')
            return Response(json.dumps(response, cls=ResponseEncoder), status=500, mimetype='application/json')

        try:
            relative_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.' + extension)
            absolute_filename = os.path.abspath(relative_filename)
            file.save(relative_filename)
            response.url = filename
            if extension not in app.config['NO_EXTENSION_TYPES']:
                response.url += '.' + extension

            # TODO use API key for user
            if file.content_length > app.config['MAX_FILESIZE_MB']*1000000 or \
                    (current_user.is_anonymous and file.content_length > app.config['MAX_ANONYMOUS_FILESIZE_MB']*1000000):
                if current_user.is_anonymous:
                    response.errors.append('Filesize ' + str(file.content_length/1000000) + ' > ' + app.config['MAX_ANONYMOUS_FILESIZE_MB'] + ' MB')
                else:
                    response.errors.append('Filesize ' + str(file.content_length/1000000) + ' > ' + app.config['MAX_FILESIZE_MB'] + ' MB')
                return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

            # Make sure they didn't lie in content_length
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            if file_length > app.config['MAX_FILESIZE_MB']*1000000 or \
                    (current_user.is_anonymous and file_length > app.config['MAX_ANONYMOUS_FILESIZE_MB']*1000000):
                if current_user.is_anonymous:
                    response.errors.append('Filesize ' + str(file_length/1000000) + ' > ' + app.config['MAX_ANONYMOUS_FILESIZE_MB'] + ' MB')
                else:
                    response.errors.append('Filesize ' + str(file_length/1000000) + ' > ' + app.config['MAX_FILESIZE_MB'] + ' MB')
                return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

            from lmda.models import File, User
            if current_user.is_anonymous:
                if not app.config["ANONYMOUS_UPLOAD"]:
                    response.errors.append('You must be signed in')
                    return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

                cur_uid = -1
            else:
                cur_uid = current_user.id
            file = File(owner=cur_uid, name=filename, extension=extension, encrypted=False, local_name=file.filename,
                        has_thumbnail=False)
            db.session.add(file)
            db.session.commit()

            # SUCCESS !!!

            # Create thumbnail
            if not current_user.is_anonymous and extension in app.config['THUMBNAIL_TYPES']:
                from lmda.models import Thumbnail
                thumbnail_process_pool.apply_async(
                    create_thumbnail,
                    args=(absolute_filename, filename),
                    callback=add_thumbnail
                )

            return Response(json.dumps(response, cls=ResponseEncoder), mimetype='application/json')
        except IOError as e:
            sys.stderr.write(str(e))
            sys.stderr.write('\n')
            response.errors.append('Error saving file')
            response.errors.append(str(e))
            return Response(json.dumps(response, cls=ResponseEncoder), status=500, mimetype='application/json')
    else:
        response.errors.append('No file sent')
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')


def gen_filename(max_tries=5, start_length=3, tries_per_len_incr=3):
    tries = 0
    while True:
        if tries >= max_tries:
            return None

        extra_length = int(tries/tries_per_len_incr)

        filename = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(start_length + extra_length))

        if Paste.by_name(filename) is not None:
            tries += 1
            continue

        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.isfile(path):  # file exists
            tries += 1
            continue

        if app.config.get('ALLOWED_TYPES', None) is not None:
            for extension in app.config['ALLOWED_TYPES']:
                if os.path.isfile(path + '.' + extension):  # file exists
                    tries += 1
                    continue
        else:
            if os.path.isfile(path):
                return None

        return filename


def add_thumbnail(result):
    if result is not False:
        outname, name, width, height = result

        from lmda.models import File

        thumbnail = Thumbnail(parent_name=name, width=width, height=height, url=outname)
        file = File.by_name(name)
        file.has_thumbnail = True
        db.session.add(thumbnail)
        db.session.commit()

db.create_all()