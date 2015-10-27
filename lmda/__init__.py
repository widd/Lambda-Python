import datetime
import time
import pytz
import json
import logging
from multiprocessing.pool import Pool
import os
from wsgiref.handlers import format_date_time
from flask import Flask
from flask.ext import assets
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from webassets import Bundle
from webassets.filter import get_filter

script_start_time = datetime.datetime.utcnow()
gmt_timezone = pytz.timezone('GMT')
start_last_modified = format_date_time(time.mktime(script_start_time.replace(tzinfo=pytz.utc).astimezone(gmt_timezone).timetuple()))

thumbnail_process_pool = Pool(2)

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

_script_dir = os.path.dirname(os.path.realpath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + _script_dir + '/dev.db'

# Relative path of where to put uploads
app.config['UPLOAD_FOLDER'] = 'uploads'
# Extensions that are allowed as uploads
app.config['ALLOWED_TYPES'] = [
    'png', 'gif', 'jpg', 'jpeg', 'webp', 'tiff', 'svg',
    'mp3', 'ogg', 'opus',
    'mp4', 'webm',
    'pdf', 'docx', 'pptx', 'xlsx', 'odt', 'ods', 'odt'
]
# Extensions to omit the extension of when linking
app.config['NO_EXTENSION_TYPES'] = ['png', 'jpg', 'jpeg', 'gif', 'mp3']
# Types to attempt to make a thumbnail for
app.config['THUMBNAIL_TYPES'] = ['png', 'jpg', 'jpeg', 'gif', 'tiff', 'webp', 'svg']
# Images to use in replacement of a thumbnail for types
app.config['GENERIC_IMAGES'] = {
    'png': '/static/img/generic/image.svg',
    'jpg': '/static/img/generic/image.svg',
    'jpeg': '/static/img/generic/image.svg',
    'tiff': '/static/img/generic/image.svg',
    'webp': '/static/img/generic/image.svg',
    'svg': '/static/img/generic/image.svg',
    'mp4': '/static/img/generic/video.svg',
    'webm': '/static/img/generic/video.svg',
    'avi': '/static/img/generic/video.svg',
    'm4v': '/static/img/generic/video.svg',
    'm4a': '/static/img/generic/audio.svg',
    'opus': '/static/img/generic/audio.svg',
    'ogg': '/static/img/generic/audio.svg',
    'mp3': '/static/img/generic/audio.svg',
}
# Generic image used for an extension that doesn't have another generic image
app.config['ULTIMATE_GENERIC_IMAGE'] = '/static/img/generic/generic.svg'
# Whether to allow uploading as an anonymous user
app.config['ANONYMOUS_UPLOAD'] = False
# Whether to allow pasting as an anonymous user
app.config['ANONYMOUS_PASTE'] = True  # TODO has no effect
# Maximum filesize (in MB) for an upload by an authenticated user
app.config['MAX_FILESIZE_MB'] = 20
# Maximum filsize (in MB) for an upload by an anonymous user
app.config['MAX_ANONYMOUS_FILESIZE_MB'] = 5
# What to prepend links to uploads with
app.config['UPLOAD_DOMAIN'] = "/"
# Secret key used for sessions and stuff
app.config['SECRET_KEY'] = 'SUPER_SECRET'
# Whether to use ReCaptcha or not
app.config['RECAPTCHA'] = True
# ReCaptcha secret key
app.config['RECAPTCHA_SECRET'] = 'SUPER_SECRET'
# ReCaptcha public key
app.config['RECAPTCHA_PUBLIC'] = 'SUPER_SECRET'

if os.environ.get('LAMBDA_CONFIG') is not None:
    app.config.from_envvar('LAMBDA_CONFIG')

# The following lines shouldn't be user-configurable, and are based off of user-configurable options
app.config['MAX_CONTENT_LENGTH'] = app.config['MAX_FILESIZE_MB'] * 1024 * 1024
if not app.config['RECAPTCHA_PUBLIC'] or not app.config['RECAPTCHA_SECRET']:
    print('ReCaptcha public and private keys are not both defined. Disabling ReCaptcha.')
    app.config['RECAPTCHA'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(userid):
    from lmda.models import User
    return User.by_id(userid)

# Setup assets
asset_env = assets.Environment(app)
# stylesheets
sass_filter = get_filter('sass', as_output=True, load_paths='static/src/sass')
main_css = Bundle('src/sass/all.sass', filters=sass_filter, output='css/all.css')
index_css = Bundle('src/sass/index.sass', filters=sass_filter, output='css/index.css')
form_css = Bundle('src/sass/form.sass', filters=sass_filter, output='css/form.css')
codemirror_css = Bundle('src/css/codemirror.css', 'src/css/codemirror-zenburn.css', filters='yui_css', output='css/codemirror.css')
paste_css = Bundle('src/sass/paste.sass', filters=sass_filter, output='css/paste.css')
about_css = Bundle('src/sass/about.sass', filters=sass_filter, output='css/about.css')
upload_css = Bundle('src/sass/upload.sass', filters=sass_filter, output='css/upload.css')
error_css = Bundle('src/sass/error.sass', filters=sass_filter, output='css/error.css')
past_upload_css = Bundle('src/sass/pastUploads.sass', filters=sass_filter, output='css/pastUploads.css')
asset_env.register('main_css', main_css)
asset_env.register('index_css', index_css)
asset_env.register('form_css', form_css)
asset_env.register('codemirror_css', codemirror_css)
asset_env.register('paste_css', paste_css)
asset_env.register('about_css', about_css)
asset_env.register('upload_css', upload_css)
asset_env.register('error_css', error_css)
asset_env.register('past_upload_css', past_upload_css)
# scripts
codemirror_js = Bundle('src/js/codemirror.js', 'src/js/codemirror-python.js', output='js/codemirror.js')
sjcl = Bundle('src/js/sjcl.js', output='js/sjcl.js')
all_js = Bundle('src/coffee/all.coffee', filters='coffeescript', output='js/all.js')
paste_js = Bundle('src/coffee/paste.coffee', filters='coffeescript', output='js/paste.js')
login_js = Bundle('src/coffee/login.coffee', filters='coffeescript', output='js/login.js')
register_js = Bundle('src/coffee/register.coffee', filters='coffeescript', output='js/register.js')
upload_js = Bundle('src/coffee/upload.coffee', filters='coffeescript', output='js/upload.js')
past_upload_js = Bundle('src/coffee/pastUploads.coffee', filters='coffeescript', output='js/pastUploads.js')
manage_account_js = Bundle('src/coffee/manageAccount.coffee', filters='coffeescript', output='js/manageAccount.js')
admin_upload_manage_js = Bundle('src/coffee/adminUploadManage.coffee', filters='coffeescript', output='js/adminUploadManage.js')
asset_env.register('codemirror_js', codemirror_js)
asset_env.register('all_js', all_js)
asset_env.register('paste_js', paste_js)
asset_env.register('login_js', login_js)
asset_env.register('register_js', register_js)
asset_env.register('upload_js', upload_js)
asset_env.register('past_upload_js', past_upload_js)
asset_env.register('manage_account_js', manage_account_js)
asset_env.register('admin_upload_manage_js', admin_upload_manage_js)
asset_env.register('sjcl', sjcl)


class ResponseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)
        values = obj.__dict__
        return values


import lmda.views

with app.app_context():
    lmda.views.create_static_html()
