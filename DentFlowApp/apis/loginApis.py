from logging import addLevelName

from DentFlowApp import app
from flask import request, redirect, render_template
from flask_login import login_user, logout_user, current_user, AnonymousUserMixin
from DentFlowApp import login
from DentFlowApp.dao import userDao
from DentFlowApp.models import UserRole
from DentFlowApp.admin import admin


@app.route("/")
def hello_world():
    can_do = {}
    if current_user.is_authenticated:
        if current_user.vai_tro == UserRole.USER:
            can_do['Hồ sơ của tôi'] = '#'
            can_do['Lịch hẹn của tôi'] = '#'
        else:
            for item in admin.menu():
                if item.is_accessible():
                    if item.name != 'Home' and item.name != 'Đăng xuất':
                        can_do[item.name] = item.get_url()
    print(can_do)
    return render_template("index.html", can_do=can_do)

@app.route('/login')
def login_view():
    return render_template('login.html')

@app.route('/register')
def register_view():
    return render_template('register.html')

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
    return redirect('/')


@app.route('/logout-admin')
def logout_admin():
    logout_user()
    return redirect('/admin')


@login.user_loader
def load_user(user_id):
    return userDao.get_user_by_id(user_id)
