import os
from flask import render_template, send_file, session
from lmda import app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/generic/by-ext/<extension>')
def generic_by_ext(extension):
    generic_path = app.config['GENERIC_IMAGES'].get(extension, app.config['ULTIMATE_GENERIC_IMAGE'])
    return send_file(os.getcwd() + '/lmda' + generic_path)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='Nothing\'s Here'), 404


@app.before_request
def make_session_permanent():
    session.permanent = True