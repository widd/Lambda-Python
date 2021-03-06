import datetime
import json
import random
import string
from flask import request, render_template, Response
from flask_login import login_user, current_user, logout_user
from passlib.context import CryptContext
from lmda import app, ResponseEncoder, db, start_last_modified, recaptcha

pwd_context = CryptContext(
    schemes=["django_pbkdf2_sha256"],
    default="django_pbkdf2_sha256",

    all__vary_rounds="10%",

    django_pbkdf2_sha256__default_rounds=12000
)


class EmptyClass:
    pass


@app.route('/login')
def login():
    if 'If-Modified-Since' in request.headers:
        if request.headers['If-Modified-Since'] == start_last_modified:
            return Response(status=304)

    response = Response(render_template('login.html'))
    response.headers['Last-Modified'] = start_last_modified

    return response


@app.route('/register')
def register():
    if 'If-Modified-Since' in request.headers:
        if request.headers['If-Modified-Since'] == start_last_modified:
            return Response(status=304)

    response = Response(render_template('register.html'))
    response.headers['Last-Modified'] = start_last_modified

    return response


@app.route('/api/session', methods=['DELETE'])
def log_out():
    response = EmptyClass()
    response.errors = []

    logout_user()
    return Response(json.dumps(response, cls=ResponseEncoder), mimetype='application/json')


@app.route('/api/session', methods=['GET'])
def get_session_info():
    response = EmptyClass()
    response.errors = []

    from lmda.models import User

    user = current_user
    if user is None or user.is_anonymous:
        api_key = request.args.get('api_key')
        if api_key is not None:
            user = User.by_api_key(api_key)

    if user is None or user.is_anonymous:
        response.errors.append('No session cookie or api_key. Did you forget to log in?')
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

    response.id = user.id
    response.username = user.username
    response.api_key = user.api_key

    return Response(json.dumps(response, cls=ResponseEncoder), mimetype='application/json')


@app.route('/user/manage')
def manage_user():
    if 'If-Modified-Since' in request.headers:
        if request.headers['If-Modified-Since'] == start_last_modified:
            return Response(status=304)

    response = Response(render_template('manageAccount.html'))
    response.headers['Last-Modified'] = start_last_modified

    return response


@app.route('/api/user/new', methods=['POST'])
def create_user():
    response = EmptyClass()
    response.errors = []

    username = request.form.get('username')
    password = request.form.get('password')

    # Begin check that all data has been sent
    if not username:
        response.errors.append('No username sent')
    if not password:
        response.errors.append('No password sent')

    if len(response.errors) > 0:
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')
    # End check that all data has been checked

    # Begin input validity checks
    # Validate username input
    if not username.isalnum():
        response.errors.append('Username is not alphanumeric')
    if len(username) > 16:
        response.errors.append('Username length > 16')

    # Validate password input
    if len(password) < 6:
        response.errors.append('Password length < 6')
    if len(password) > 64:
        response.errors.append('Password length > 64')

    # Return out if any input validity errors occurred
    if len(response.errors) > 0:
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')
    # End input validity checks

    # Check captcha
    if not recaptcha.verify():
        response.errors.append('Incorrect captcha')
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

    from lmda.models import User
    if User.by_name(username) is not None:
        response.errors.append('User already exists with username')
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

    # All checks passed, go through with register
    pass_hash = pwd_context.encrypt(password)
    api_key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for i in range(32))
    # TODO verify uniqueness. Right now SQL will fail very ungracefully.

    from lmda.models import User
    user = User(username=username, password=pass_hash, creation_date=datetime.datetime.utcnow(), api_key=api_key,
                encryption_enabled=False)
    db.session.add(user)
    db.session.commit()

    login_user(user)

    response.api_key = user.api_key
    response.success = True
    return Response(json.dumps(response, cls=ResponseEncoder), mimetype='application/json')


@app.route('/api/user/login', methods=['POST'])
def auth_user():
    response = EmptyClass()
    response.errors = []

    username = request.form.get('username')
    password = request.form.get('password')

    # Begin check that all data has been sent
    if not username:
        response.errors.append('No username sent')
    if not password:
        response.errors.append('No password sent')

    if len(response.errors) > 0:
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')
    # End check that all data has been sent

    from lmda.models import User
    user = User.by_name(username)

    if user is None:
        response.errors.append('No such user')
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

    if not pwd_context.verify(password, user.password):
        response.errors.append('Wrong password')
        return Response(json.dumps(response, cls=ResponseEncoder), status=400, mimetype='application/json')

    login_user(user)

    response.api_key = user.api_key
    response.success = True
    return Response(json.dumps(response, cls=ResponseEncoder), mimetype='application/json')
