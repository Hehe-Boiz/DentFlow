from logging import addLevelName

from sqlalchemy.exc import IntegrityError

from DentFlowApp import app,db, bcrypt
from flask import request, redirect, render_template, session, flash
from flask_login import login_user, logout_user, current_user, AnonymousUserMixin
from DentFlowApp import login
from DentFlowApp.dao import user_dao
from DentFlowApp.models import UserRole, NguoiDung
from DentFlowApp.admin import admin
from DentFlowApp import utils

@app.route("/")
def index():
    return render_template("index.html")

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
    print(password)
    u = user_dao.auth_user(username=username, password=password)
    if u:
        login_user(user=u)
        session['can_do'] = utils.user_can_do(u)
        if u.vai_tro == UserRole.DOCTOR:
            return redirect('/treatment')

    next = request.args.get('next')
    print(next)
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
        user_dao.add_user(ho_ten=data.get('name'), so_dien_thoai=data.get('phone'), username=data.get('username'), password=password, avatar=request.files.get('avatar'))
        u = user_dao.auth_user(username=data.get('username'), password=password)
        if u:
            login_user(user=u)
            session['can_do'] = utils.user_can_do(u)
        return redirect('/')
    except IntegrityError as e:
        db.session.rollback()
        return render_template('register.html', err_msg="Tên người dùng hiện tại đã trùng")
    except Exception as ex:
        return render_template('register.html', err_msg=str(ex))


@app.route('/logout')
def logout_process():
    del session['can_do']
    logout_user()
    return redirect('/')


@app.route('/logout-admin')
def logout_admin():
    logout_user()
    return redirect('/admin')


@app.route('/change-password', methods=['POST'])
def change_password():
    username = request.form.get('username')
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    u = user_dao.auth_user(username=username, password=old_password)

    if u:
        if new_password != confirm_password:
            err_msg = 'Mật khẩu mới không khớp với nhau!'
            flash(err_msg, 'failed')
            return redirect('/user')
        hashed_password = bcrypt.generate_password_hash(new_password.strip()).decode('utf-8')
        user_dao.update_user(user=u,password=hashed_password)
        flash('Đổi mật khẩu thành công', 'failed')
        return redirect('/user')
    else:
        flash('Mật khẩu tài khoản hiện tại không khớp', 'failed')
        return redirect('/user')


@login.user_loader
def load_user(user_id):
    return user_dao.get_user_by_id(user_id)



