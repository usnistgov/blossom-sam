#!/usr/bin/env python3
from flask import (
    Flask,
    jsonify,
    redirect,
    request,
    response
)

app = Flask(__name__)

@app.route('/')
def endpoint_root():
    return Response('BLoSS@M SAM Service Running...', mimetype='text/plain')
