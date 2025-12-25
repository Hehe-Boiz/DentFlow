import math
from logging import addLevelName

from sqlalchemy.exc import IntegrityError

from DentFlowApp import app,db, bcrypt
from flask import request, redirect, render_template, session, flash
from flask_login import login_user, logout_user, current_user, AnonymousUserMixin
from DentFlowApp import login
from DentFlowApp.dao import user_dao, dichvu_dao, lich_hen_dao
from DentFlowApp.models import UserRole, NguoiDung
from DentFlowApp.admin import admin
from DentFlowApp import utils


@app.route("/")
def index():
    dich_vu = dichvu_dao.get_dich_vu()
    return render_template("index.html",dich_vu=dich_vu)
@app.route("/dich_vu")
def dichvu_view():
    page = request.args.get('page', 1)
    dich_vu = dichvu_dao.get_dich_vu(page=int(page))
    return render_template("dich_vu.html",dich_vu=dich_vu,
                           pages=math.ceil(dichvu_dao.get_tong_dich_vu() / app.config['PAGE_SIZE']))

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
    else:
        flash("Đăng nhập thất bại", 'danger')
        return redirect('/login')

    next = request.args.get('next')
    print(next)
    flash("Đăng nhập thành công", 'success')
    return redirect(next if next else '/')

@app.route('/register', methods=['post'])
def register_process():
    data = request.form
    password = data.get('password')
    confirm = data.get('confirm')
    ho_ten = data.get('name')
    so_dien_thoai = data.get('phone')
    avatar = request.files.get('avatar')
    is_valid, error_msg = utils.validate_thong_tin_benh_nhan(ho_ten=ho_ten, sdt=so_dien_thoai,
                                                             password=password,
                                                             confirm_password=confirm)
    if not is_valid:
        prev_info = {
            'username': data.get('username'),
            'name': ho_ten,
            'phone': so_dien_thoai,
            'password': password,
            'confirm': confirm,
        }
        flash(error_msg, 'failed')
        return render_template('register.html', prev_info=prev_info)

    try:
        user_dao.add_user(ho_ten=ho_ten, so_dien_thoai=so_dien_thoai, username=data.get('username'), password=password, avatar=avatar)
        u = user_dao.auth_user(username=data.get('username'), password=password)
        if u:
            login_user(user=u)
            session['can_do'] = utils.user_can_do(u)
        flash("Đăng ký người dùng thành công", 'success')
        return redirect('/')
    except IntegrityError as e:
        db.session.rollback()
        flash("Tên người dùng hiện tại đã trùng", 'danger')
        return render_template('register.html')
    except Exception as ex:
        flash(str(ex), 'failed')
        return render_template('register.html')


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
        flash('Mật khẩu tài khoản hiện tại không khớp', 'danger')
        return redirect('/user')


@login.user_loader
def load_user(user_id):
    return user_dao.get_user_by_id(user_id)



