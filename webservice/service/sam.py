#!/usr/bin/env python3
from flask import (
    Flask,
    jsonify,
    redirect,
    request,
    Response,
    send_file
)

from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

app = Flask(__name__)

# TODO: Move this to a configuration file later.
INSTALLER_BASE = '/opt/blossom-sam/installers'
KEYFILES_BASE = '/opt/blossom-sam/keys'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/blossom-sam/sam.db'

db = SQLAlchemy(app)

try:
    from service.db_model import *
except:
    from db_model import *

@app.route('/')
def endpoint_root():
    return Response('BLoSS@M SAM Service Running...', mimetype='text/plain')

@app.route('/installer')
def endpoint_getInstaller():
    p = Path(INSTALLER_BASE) / 'installer.zip'
    if not p.exists():
        return Response('', mimetype='text/plain'), 503

    return send_file(p, mimetype='application/zip', as_attachment=True,
                     etag=True)

@app.route('/installer/<string:os>/<string:arch>/<string:name>/<string:ver>')
def endpoint_inst(os, arch, name, ver):
    auth = request.headers.get('Authorization')
    if not auth:
        return Response('', mimetype='text/plain'), 401

    spauth = auth.split()
    if len(spauth) != 2:
        return Response('', mimetype='text/plain'), 400

    if spauth[0] != 'Bearer':
        return Response('', mimetype='text/plain'), 401

    # Look up token in db and find the machine it belongs to.
    sys = System.query.filter_by(token=spauth[1])
    if not sys:
        return Response('', mimetype='text/plain'), 401

    # Make sure we know about this application
    a = Application.query.filter_by(os=os, arch=arch, name=name, version=ver)
    if not a:
        return Response('', mimetype='text/plain'), 404

    # See if we have a directory for this particular request
    p = Path(INSTALLER_BASE)
    p2 = p / os / arch / app / ver / 'sam.pkg'
    if not p2.exists():
        return Response('', mimetype='text/plain'), 404

    # Send the installer out
    return send_file(p2, mimetype='application/zip', as_attachment=True,
                     download_name=app + '-' + ver + '.pkg', etag=True)

@app.route('/key/<string:os>/<string:arch>/<string:app>/<string:ver>')
def endpoint_key(os, arch, app, ver):
    auth = request.headers.get('Authorization')
    if not auth:
        return Response('', mimetype='text/plain'), 401

    spauth = auth.split()
    if len(spauth) != 2:
        return Response('', mimetype='text/plain'), 400

    if spauth[0] != 'Bearer':
        return Response('', mimetype='text/plain'), 401

    # Look up token in db and find the machine it belongs to.
    sys = System.query.filter_by(token=spauth[1])
    if not sys:
        return Response('', mimetype='text/plain'), 401

    # Make sure we know about this application
    a = Application.query.filter_by(os=os, arch=arch, name=name, version=ver)
    if not a:
        return Response('', mimetype='text/plain'), 404

    # See if we have a key for this particular request
    # TODO: grab keys from db.
    p = Path(INSTALLER_BASE)
    p2 = p / os / arch / app / ver / 'key.bin'
    if not p2.exists():
        return Response('', mimetype='text/plain'), 404

    # Send the key out
    return send_file(p2, mimetype='application/octet-stream',
                     as_attachment=True, download_name=app + '-' + ver + '.key',
                     etag=True)

################################################################################
# If the script is being run directly, set up our server.                      #
################################################################################
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, use_evalex=False)
