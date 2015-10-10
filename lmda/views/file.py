import os
from flask import send_from_directory
from lmda import app
from lmda.views import paste


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
