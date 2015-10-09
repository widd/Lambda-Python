import json
from flask import Flask
from flask.ext import assets
from flask.ext.login import LoginManager
from webassets import Bundle
from webassets.filter import get_filter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_TYPES'] = ['png', 'jpg', 'jpeg']
app.config['ANONYMOUS_UPLOAD'] = True
app.config['ANONYMOUS_PASTE'] = True
app.config['MAX_FILESIZE_MB'] = 20
app.config['MAX_ANONYMOUS_FILESIZE_MB'] = 6
app.config['UPLOAD_DOMAIN'] = "/"
app.config['SECRET_KEY'] = 'SUPER_SECRET'

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
asset_env.register('main_css', main_css)
asset_env.register('index_css', index_css)
asset_env.register('form_css', form_css)
asset_env.register('codemirror_css', codemirror_css)
asset_env.register('paste_css', paste_css)
asset_env.register('about_css', about_css)
asset_env.register('upload_css', upload_css)
asset_env.register('error_css', error_css)
# scripts
codemirror_js = Bundle('src/js/codemirror.js', 'src/js/codemirror-python.js', output='js/codemirror.js')
sjcl = Bundle('src/js/sjcl.js', output='js/sjcl.js')
all_js = Bundle('src/coffee/all.coffee', filters='coffeescript', output='js/all.js')
paste_js = Bundle('src/coffee/paste.coffee', filters='coffeescript', output='js/paste.js')
login_js = Bundle('src/coffee/login.coffee', filters='coffeescript', output='js/login.js')
upload_js = Bundle('src/coffee/upload.coffee', filters='coffeescript', output='js/upload.js')
asset_env.register('codemirror_js', codemirror_js)
asset_env.register('all_js', all_js)
asset_env.register('paste_js', paste_js)
asset_env.register('login_js', login_js)
asset_env.register('upload_js', upload_js)
asset_env.register('sjcl', sjcl)


class ResponseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)
        values = obj.__dict__
        return values


import lmda.views
