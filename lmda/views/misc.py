from flask import render_template
from lmda import app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='Nothing\'s Here'), 404
