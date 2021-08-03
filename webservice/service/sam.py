#!/usr/bin/env python3
from flask import (
    Flask,
    jsonify,
    redirect,
    request,
    Response,
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

@app.route('/installer')
def endpoint_getInstaller():
    p = Path(INSTALLER_BASE) / 'installer.zip'
    if not p.exists():
        return Response('', mimetype='text/plain'), 503

    return send_file(p, mimetype='application/zip', as_attachment=True,
                     etag=True)

# TODO: Implement authentication of clients connecting to below endpoints
@app.route('/installer/<string:os>/<string:arch>/<string:app>/<string:ver>')
def endpoint_inst(os, arch, app, ver):
    # See if we have a directory for this particular request
    p = Path(INSTALLER_BASE)
    p2 = p / os / arch / app / ver / 'sam.pkg'
    if not p2.exists():
        return Response('', mimetype='text/plain'), 404

    # Send the installer out
    return send_file(p2, mimetype='application/zip', as_attachment=True,
                     download_name=app + '-' + ver + '.pkg', etag=True)


# If the script is being run directly, set up our server.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, use_evalex=False)
