import os
from flask import render_template
from lmda.views import auth, misc, paste, upload, file


def create_static_html():
    for filename in os.listdir('lmda/templates'):
        print("Compiling %s" % filename)
        compiled = render_template(filename)
        with open('lmda/static/shtml/%s' % filename, 'w') as outfile:
            outfile.write(compiled)
