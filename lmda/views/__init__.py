import os
from flask import render_template
from lmda.views import auth, misc, paste, upload, file, admin


def create_static_html():
    shtml_dir = 'lmda/static/shtml'
    if not os.path.exists(shtml_dir):
        os.makedirs(shtml_dir)

    for filename in os.listdir('lmda/templates'):
        print("Compiling %s" % filename)
        compiled = render_template(filename)
        filepath = 'lmda/static/shtml/%s' % filename
        with open(filepath, 'w') as outfile:
            outfile.write(compiled.encode('utf-8'))
