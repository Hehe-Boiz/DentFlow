from flask_admin import BaseView, expose

from DentFlowApp import app
from flask import render_template, request,redirect
from flask_login import login_user, logout_user
from DentFlowApp import login
from DentFlowApp.dao import userDao


@app.route("/")
def hello_world():
    return "Hello World!!!"


@app.route('/login', methods=['post'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')

    u = userDao.auth_user(username=username, password=password)
    if u:
        login_user(user=u)

    next = request.args.get('next')
    return redirect(next if next else '/')


@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')


@app.route('/logout-admin')
def logout_admin():
    logout_user()
    return redirect('/admin')


@login.user_loader
def load_user(user_id):
    return userDao.get_user_by_id(user_id)
