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
from flask_bcrypt import Bcrypt
from pathlib import Path
import base64
import traceback

app = Flask(__name__)

# TODO: Move this to a configuration file later.
INSTALLER_BASE = '/opt/blossom-sam/installers'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/blossom-sam/sam.db'
app.config['BCRYPT_HANDLE_LONG_PASSWORDS'] = True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

try:
    from service.db_model import *
except:
    from db_model import *

try:
    from service.blossom import *
except:
    from blossom import *

def add_admin(username, password):
    added = False
    hash = base64.b64encode(bcrypt.generate_password_hash(password))
    newadmin = Admin(username=username, passwd=hash)

    try:
        db.session.add(newadmin)
        db.session.commit()
        added = True
    except:
        db.session.rollback()
        added = False

    return added

def add_system(name, token):
    added = False
    newsys = System(name=name, token=token)

    try:
        db.session.add(newsys)
        db.session.commit()
        added = True
    except:
        db.session.rollback()
        added = False

    return added

@app.route('/')
def endpoint_root():
    return Response('BLoSS@M SAM Service Running...\n', mimetype='text/plain')

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
        return Response('Unauthorized\n', mimetype='text/plain'), 401

    spauth = auth.split()
    if len(spauth) != 2:
        return Response('Unauthorized\n', mimetype='text/plain'), 401

    if spauth[0] != 'Bearer':
        return Response('Unauthorized\n', mimetype='text/plain'), 401

    # Look up token in db and find the machine it belongs to.
    sys = System.query.filter_by(token=spauth[1]).all()
    if not sys or len(sys) != 1:
        return Response('Unauthorized\n', mimetype='text/plain'), 401

    # Make sure we know about this application
    a = Application.query.filter_by(os=os, arch=arch, name=name, version=ver).all()
    if not a or len(a) != 1:
        return Response('Application not found!\n', mimetype='text/plain'), 404

    # See if we have a directory for this particular request
    p = Path(INSTALLER_BASE)
    p2 = p / os / arch / name / ver / 'sam.pkg'
    if not p2.exists():
        return Response('Installer not found!\n', mimetype='text/plain'), 404

    # Send the installer out
    return send_file(str(p2), mimetype='application/zip', as_attachment=True)

@app.route('/key/<string:os>/<string:arch>/<string:name>/<string:ver>')
def endpoint_key(os, arch, name, ver):
    auth = request.headers.get('Authorization')
    if not auth:
        return Response('Unauthorized\n', mimetype='text/plain'), 401

    spauth = auth.split()
    if len(spauth) != 2:
        return Response('Unauthorized\n', mimetype='text/plain'), 401

    if spauth[0] != 'Bearer':
        return Response('Unauthorized\n', mimetype='text/plain'), 401

    # Look up token in db and find the machine it belongs to.
    sys = System.query.filter_by(token=spauth[1]).all()
    if not sys or len(sys) != 1:
        return Response('Unauthorized\n', mimetype='text/plain'), 401

    # Make sure we know about this application
    a = Application.query.filter_by(os=os, arch=arch, name=name, version=ver).all()
    if not a or len(a) != 1:
        return Response('Application not found!\n', mimetype='text/plain'), 404

    leased = False
    for k in a[0].keys:
        if k.leased_to is None:
            try:
                k.leased_to = sys[0]
                db.session.commit()
                leased = True
                break
            except:
                pass

    if not leased:
        return Response('No keys available!\n', mimetype='text/plain'), 402

    # Send the key out
    resp = Response(base64.b64decode(k.data),
                    mimetype='application/octet-stream')
    resp.headers.set('Content-Disposition', 'attachment; filename=' +
                     name + '-' + ver + '.key')
    return resp, 200

@app.route('/swid/<string:os>/<string:arch>/<string:name>/<string:ver>', methods=['POST'])
def endpoint_swid(os, arch, name, ver):
    auth = request.headers.get('Authorization')
    if not auth:
        return Response('Unauthorized\n', mimetype='text/plain'), 401

    spauth = auth.split()
    if len(spauth) != 2:
        return Response('Unauthorized\n', mimetype='text/plain'), 401

    if spauth[0] != 'Bearer':
        return Response('Unauthorized\n', mimetype='text/plain'), 401

    # Look up token in db and find the machine it belongs to.
    sys = System.query.filter_by(token=spauth[1]).all()
    if not sys or len(sys) != 1:
        return Response('Unauthorized\n', mimetype='text/plain'), 401

    # Grab the tag and decode it
    swid_tag = request.form.get('SWID_TAG')
    if not swid_tag:
        return Response('Bad Request\n', mimetype='text/plain'), 400

    swid_tag_decoded = base64.urlsafe_b64decode(swid_tag)

    # Make sure we know about this application
    a = Application.query.filter_by(os=os, arch=arch, name=name, version=ver).all()
    if not a or len(a) != 1:
        return Response('Application not found!\n', mimetype='text/plain'), 404

    # Add the new tag to the db.
    try:
        newtag = SwidTag(application=a[0], system=sys[0], swid_tag=swid_tag)
        db.session.add(newtag)
        db.session.commit()
    except:
        return Response('System Error\n', mimetype='text/plain'), 500

    return Response('Tag Added\n', mimetype='text/plain'), 201

@app.route('/admin/addSoftware', methods=['POST'])
def endpoint_addSoftware():
    auth = request.authorization
    if not auth:
        return Response('', mimetype='text/plain'), 401

    users = Admin.query.filter_by(username=auth.username).all()
    if not users or len(users) != 1:
        return Response('', mimetype='text/plain'), 401

    if not bcrypt.check_password_hash(base64.b64decode(users[0].passwd), auth.password):
        return Response('', mimetype='text/plain'), 401

    json_data = request.get_json()
    if not json_data:
        return Response('', mimetype='text/plain'), 400

    try:
        name = json_data['name']
        ver = json_data['version']
        arch = json_data['arch']
        os = json_data['os']
        blossom_id = json_data['blossom_asset']

        newapp = Application(name=name, version=ver, arch=arch, os=os,
                             blossom_id=blossom_id)
        db.session.add(newapp)
        db.session.commit()
        return Response('', mimetype='text/plain'), 201
    except:
        db.session.rollback()
        return Response('', mimetype='text/plain'), 500

@app.route('/admin/reqKeys/<string:os>/<string:arch>/<string:name>/<string:ver>',
           methods=['POST'])
def endpoint_reqKey(os, arch, name, ver):
    auth = request.authorization
    if not auth:
        return Response('', mimetype='text/plain'), 401

    users = Admin.query.filter_by(username=auth.username).all()
    if not users or len(users) != 1:
        return Response('', mimetype='text/plain'), 401

    if not bcrypt.check_password_hash(base64.b64decode(users[0].passwd), auth.password):
        return Response('', mimetype='text/plain'), 401

    json_data = request.get_json()
    if not json_data:
        return Response('', mimetype='text/plain'), 400

    ap = Application.query.filter_by(name=name, version=ver, arch=arch,
                                     os=os).all()
    if not ap or len(ap) != 1:
        return Response('', mimetype='text/plain'), 404

    try:
        count = int(json_data['count'])

        if count < 1:
            return Response('', mimetype='text/plain'), 400

        RequestCheckout(ap.blossom_id, count)
        return Response('', mimetype='text/plain'), 201
    except:
        return Response('', mimetype='text/plain'), 500

@app.route('/admin/getKeys/<string:os>/<string:arch>/<string:name>/<string:ver>')
def endpoint_getKey(os, arch, name, ver):
    auth = request.authorization
    if not auth:
        return Response('', mimetype='text/plain'), 401

    users = Admin.query.filter_by(username=auth.username).all()
    if not users or len(users) != 1:
        return Response('', mimetype='text/plain'), 401

    if not bcrypt.check_password_hash(base64.b64decode(users[0].passwd), auth.password):
        return Response('', mimetype='text/plain'), 401

    ap = Application.query.filter_by(name=name, version=ver, arch=arch,
                                     os=os).all()
    if not ap or len(ap) != 1:
        return Response('', mimetype='text/plain'), 404

    try:
        licenses = json.loads(GetLicenses(ap.blossom_id))

        for l in licenses:
            newkey = Key(application=ap[0], data=l['LicenseID'],
                         expiration=l['Expiration'])
            db.session.add(newkey)
        db.session.commit()
        return Response('', mimetype='text/plain'), 201
    except:
        db.session.rollback()
        return Response('', mimetype='text/plain'), 500

@app.route('/admin/addKey/<string:os>/<string:arch>/<string:name>/<string:ver>',
           methods=['POST'])
def endpoint_addKey(os, arch, name, ver):
    auth = request.authorization
    if not auth:
        return Response('', mimetype='text/plain'), 401

    users = Admin.query.filter_by(username=auth.username).all()
    if not users or len(users) != 1:
        return Response('', mimetype='text/plain'), 401

    if not bcrypt.check_password_hash(base64.b64decode(users[0].passwd), auth.password):
        return Response('', mimetype='text/plain'), 401

    json_data = request.get_json()
    if not json_data:
        return Response('', mimetype='text/plain'), 400

    ap = Application.query.filter_by(name=name, version=ver, arch=arch,
                                     os=os).all()
    if not ap or len(ap) != 1:
        return Response('', mimetype='text/plain'), 404

    try:
        newkey = Key(application=ap[0], data=json_data['key'],
                     expiration='Never')
        db.session.add(newkey)
        db.session.commit()
        return Response('', mimetype='text/plain'), 201
    except:
        db.session.rollback()
        return Response('', mimetype='text/plain'), 500

################################################################################
# If the script is being run directly, set up our server.                      #
################################################################################
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, use_evalex=False)
