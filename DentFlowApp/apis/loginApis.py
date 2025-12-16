from logging import addLevelName

from sqlalchemy.exc import IntegrityError

from DentFlowApp import app,db
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

@app.route('/register', methods=['post'])
def register_process():
    data = request.form
    password = data.get('password')
    confirm = data.get('confirm')
    if password != confirm:
        err_msg = 'Mật khẩu không khớp!'
        prev_info = {
            'username': data.get('username'),
            'name': data.get('name'),
            'phone': data.get('phone'),
        }
        return render_template('register.html', err_msg=err_msg, prev_info=prev_info)

    try:
        userDao.add_user(ho_ten=data.get('name'), so_dien_thoai=data.get('phone'), username=data.get('username'), password=password, avatar=request.files.get('avatar'))
        u = userDao.auth_user(username=data.get('username'), password=password)
        if u:
            login_user(user=u)
        return redirect('/')
    except IntegrityError as e:
        db.session.rollback()
        return render_template('register.html', err_msg="Tên người dùng hiện tại đã trùng")
    except Exception as ex:
        return render_template('register.html', err_msg=str(ex))


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
