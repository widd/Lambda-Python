import json
import mimetypes
import os
from flask import send_from_directory, Response, request, render_template
from flask_login import current_user
from lmda import app, start_last_modified, db
from lmda.models import Thumbnail, Authority, File
from lmda.views import paste


mimetypes.add_type('video/webm', 'webm')


class JsonResponse:
    def __init__(self):
        self.errors = []

class PastUpload:
    def __init__(self, id, name, local_name, extension, has_thumb):
        self.id = id
        self.name = name
        self.local_name = local_name
        self.extension = extension
        self.has_thumb = has_thumb


class ReturnThumbnail:
    def __init__(self, url, parent, width, height):
        self.url = url
        self.width = width
        self.height = height
        self.parent = parent


class ResponseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)
        values = obj.__dict__
        return values


@app.route('/file/<name>', methods=['DELETE'])
def delete_file(name):
    api_key = request.form.get('api_key')

    # TODO delete pastes too
    response = JsonResponse()

    user = current_user

    if user.is_anonymous and api_key is not None:
        from lmda.models import User
        user = User.by_api_key(api_key)

    if user is None or user.is_anonymous:
        response.errors = ['Not signed in']
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

    file = File.by_name(name)
    if file is None:
        response.errors = ["File doesn't exist"]
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')
    if file.owner is not user.id:
        response.errors = ['Not your file']
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

    filename = file.name + '.' + file.extension
    os.remove(os.getcwd() + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
    db.session.delete(file)
    db.session.commit()

    return Response(json.dumps(response, cls=ResponseEncoder), mimetype='application/json')


@app.route('/<name>', methods=['GET'])
def view_image(name):
    path = os.path.join(app.config['UPLOAD_FOLDER'], name)

    if '.' not in name:
        for extension in app.config['ALLOWED_TYPES']:
            if os.path.isfile(path + '.' + extension):  # file exists
                if 'If-Modified-Since' in request.headers:
                    # TODO check file mod time
                    return Response(status=304)

                return send_from_directory(os.getcwd() + '/' + app.config['UPLOAD_FOLDER'], name + '.' + extension,
                                           mimetype=mimetypes.types_map.get('.' + extension, 'application/octet-stream'))
    elif os.path.isfile(os.getcwd() + '/' + path):
        if 'If-Modified-Since' in request.headers:
            # TODO check file mod time
            return Response(status=304)

        filename, file_extension = os.path.splitext(path)
        return send_from_directory(os.getcwd() + '/' + app.config['UPLOAD_FOLDER'], name,
                                   mimetype=mimetypes.types_map.get(file_extension, 'application/octet-stream'))

    return paste.view_paste(name)


@app.route('/api/file/thumbnails/<name>')
def get_thumbnails(name):
    response = JsonResponse()

    response.thumbnails = []
    for t in Thumbnail.by_parent(name):
        response.thumbnails.append(ReturnThumbnail(t.url, t.parent_name, t.width, t.height))

    return Response(json.dumps(response, cls=ResponseEncoder), mimetype='application/json')


@app.route('/api/admin/uploads')
def get_admin_uploads():
    api_key = request.form.get('api_key')

    n = int(request.args.get('n', 10))
    page_num = int(request.args.get('page', 1))
    searchText = request.args.get('nameContains', None)
    owner_username = request.args.get('ownerUsername')

    n = max(min(n, 50), 1)  # Clamp n between 1 and 50

    user = current_user

    if user.is_anonymous and api_key is not None:
        from lmda.models import User
        user = User.by_api_key(api_key)

    response = JsonResponse()

    if user is None or user.is_anonymous:
        response.errors = ['Not signed in']
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

    authority = Authority.by_user_id(user.id)
    if authority is None:
        response.errors = ['No authority']
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

    from lmda.models import File, User

    query = File.query

    if owner_username is not None:
        target_owner = User.by_name(owner_username)
        if target_owner is not None:
            query = query.filter(File.owner == target_owner.id)

    if searchText is not None:
        query = query.filter(File.local_name.ilike('%' + searchText + '%'))

    query = query.order_by(File.id.desc())

    pagination = query.paginate(page=page_num, per_page=n)

    files = []
    for f in pagination.items:
        pu = PastUpload(f.id, f.name, f.local_name, f.extension, f.has_thumbnail)
        files.append(pu)

    response.files = files
    response.number_pages = pagination.pages
    return Response(json.dumps(response, cls=ResponseEncoder), mimetype='application/json')


@app.route('/api/user/uploads')
def get_past_uploads():
    api_key = request.form.get('api_key')

    n = int(request.args.get('n', 10))
    page_num = int(request.args.get('page', 1))
    searchText = request.args.get('nameContains', None)

    n = max(min(n, 50), 1)  # Clamp n between 1 and 50

    user = current_user

    if user.is_anonymous and api_key is not None:
        from lmda.models import User
        user = User.by_api_key(api_key)

    response = JsonResponse()

    if user is None:
        response.errors = ['Not signed in']
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

    if not current_user.is_anonymous:
        from lmda.models import File

        query = File.query.filter(File.owner == user.id).order_by(File.id.desc())
        if searchText is not None:
            query = query.filter(File.local_name.ilike('%' + searchText + '%'))

        pagination = query.paginate(page=page_num, per_page=n)

        files = []
        for f in pagination.items:
            pu = PastUpload(f.id, f.name, f.local_name, f.extension, f.has_thumbnail)
            files.append(pu)

        response.files = files
        response.number_pages = pagination.pages
        return Response(json.dumps(response, cls=ResponseEncoder), mimetype='application/json')
    else:
        response.errors = ['Not signed in']
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')


@app.route('/user/uploads')
def view_past_uploads():
    if 'If-Modified-Since' in request.headers:
        if request.headers['If-Modified-Since'] == start_last_modified:
            return Response(status=304)

    response = Response(render_template('pastUploads.html'))
    response.headers['Last-Modified'] = start_last_modified

    return response
