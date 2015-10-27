from flask import request, Response, render_template
from lmda import app, start_last_modified


@app.route('/admin/upload_manage')
def admin_upload_manage():
    if 'If-Modified-Since' in request.headers:
        if request.headers['If-Modified-Since'] == start_last_modified:
            return Response(status=304)

    response = Response(render_template('admin_upload_manage.html'))
    response.headers['Last-Modified'] = start_last_modified

    return response
