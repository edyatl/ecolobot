#!/usr/bin/env python3
import os
from app import app
from flask import render_template, send_from_directory
from flask_security import auth_required, roles_accepted, \
        current_user


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
            os.path.join(app.root_path, 'static'), 
            'favicon.ico', 
            mimetype='image/vnd.microsoft.icon'
            )


@app.route('/registered/')
@auth_required()
@roles_accepted("admin", "editor", "user")
def registered():
    res = 'User: {} successfully registered. Ask your admin for permissions.'.format(current_user.email)
    return render_template('index.html', text=res)


@app.route('/')
@auth_required()
@roles_accepted("admin", "editor")
def index():
    return render_template('index.html')

