import json
import os
from flask import send_from_directory, Response, request, render_template
from flask.ext.login import current_user
from lmda import app
from lmda.models import Thumbnail
from lmda.views import paste


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


@app.route('/<name>', methods=['GET'])
def view_image(name):
    path = os.path.join(app.config['UPLOAD_FOLDER'], name)

    if '.' not in name:
        for extension in app.config['ALLOWED_TYPES']:
            if os.path.isfile(path + '.' + extension):  # file exists
                return send_from_directory(os.getcwd() + '/' + app.config['UPLOAD_FOLDER'], name + '.' + extension)
    elif os.path.isfile(path):
        return send_from_directory(os.getcwd() + '/' + app.config['UPLOAD_FOLDER'], name)

    # TODO Serve with MIME type header of the extension of the file, to prevent uploading of not-allowed files with a fake extension

    return paste.view_paste(name)


@app.route('/api/file/thumbnails/<name>')
def get_thumbnails(name):
    response = JsonResponse()

    response.thumbnails = []
    for t in Thumbnail.by_parent(name):
        response.thumbnails.append(ReturnThumbnail(t.url, t.parent_name, t.width, t.height))

    return Response(json.dumps(response, cls=ResponseEncoder), mimetype='application/json')


@app.route('/api/user/uploads')
def get_past_uploads():
    # TODO API key support

    n = int(request.args.get('n', 10))
    page_num = int(request.args.get('page', 1))
    searchText = request.args.get('nameContains', None)

    n = max(min(n, 50), 1)  # Clamp n between 1 and 50

    response = JsonResponse()
    if not current_user.is_anonymous:
        from lmda.models import File

        query = File.query.filter(File.owner == current_user.id).order_by(File.id.desc())
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
    return render_template('pastUploads.html')
