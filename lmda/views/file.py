import os
from flask import send_file, abort
from werkzeug.utils import secure_filename
from lmda import app


@app.route('/<filename>')
def serve_file(filename):
    filename = secure_filename(filename)
    filename = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], filename)
    try:  # exact filename
        return send_file(filename)
    except FileNotFoundError:
        pass
    if '.' not in filename:
        for extension in app.config['ALLOWED_TYPES']:  # try each extension
            try:
                return send_file(filename + '.' + extension)
            except FileNotFoundError:
                pass
    abort(404)
