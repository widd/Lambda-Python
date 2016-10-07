import os
from flask import render_template, send_file, session, request, Response
from lmda import app, start_last_modified


@app.route('/')
def index():
    if 'If-Modified-Since' in request.headers:
        if request.headers['If-Modified-Since'] == start_last_modified:
            return Response(status=304)

    response = Response(render_template('index.html'))
    response.headers['Last-Modified'] = start_last_modified

    return response


@app.route('/about')
def about():
    if 'If-Modified-Since' in request.headers:
        if request.headers['If-Modified-Since'] == start_last_modified:
            return Response(status=304)

    response = Response(render_template('about.html', allowed_types=app.config['ALLOWED_TYPES']))
    response.headers['Last-Modified'] = start_last_modified

    return response


@app.route('/generic/by-ext/<extension>')
def generic_by_ext(extension):
    if 'If-Modified-Since' in request.headers:
        return Response(status=304)

    generic_path = app.config['GENERIC_IMAGES'].get(extension, app.config['ULTIMATE_GENERIC_IMAGE'])
    return send_file(os.getcwd() + '/lmda' + generic_path)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='Nothing\'s Here'), 404


@app.before_request
def make_session_permanent():
    session.permanent = True