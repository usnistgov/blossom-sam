#!/usr/bin/env python3
from flask import (
    Flask,
    jsonify,
    redirect,
    request,
    response,
    send_file
)

from pathlib import Path

app = Flask(__name__)

# TODO: Move this to a configuration file later.
INSTALLER_BASE = '/opt/blossom-sam/installers'
KEYFILES_BASE = '/opt/blossom-sam/keys'
DB_FILE = '/opt/blossom-sam/sam.db'

@app.route('/')
def endpoint_root():
    return Response('BLoSS@M SAM Service Running...', mimetype='text/plain')

# TODO: Implement authentication of clients connecting to below endpoints
@app.route('/installer/<os:string>/<arch:string>/<app:string>/<ver:string>')
def endpoint_inst(os, arch, app, ver):
    # See if we have a directory for this particular request
    p = Path(INSTALLER_BASE)
    p2 = p / os / arch / app / ver / 'sam.pkg'
    if not p2.exists():
        return Response('', mimetype='text/plain'), 404

    # Send the installer out
    return send_file(p2, mimetype='application/zip', as_attachment=True,
                     download_name=app + '-' + ver + '.pkg', etag=True)
