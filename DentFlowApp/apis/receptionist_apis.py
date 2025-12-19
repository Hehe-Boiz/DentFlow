import http
import re
from DentFlowApp import app, db
from flask import request, redirect, render_template, url_for, flash
from flask_login import current_user, login_required
from datetime import datetime
from DentFlowApp.dao import receptionistDao, user_dao
from DentFlowApp.models import UserRole, GioiTinh, HoSoBenhNhan


@app.route('/receptionist', methods=['GET'])
@login_required
def receptionist():
    flash('none')
    if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
        return render_template('receptionist/receptionist.html', letan=True, now=datetime.now().strftime("%d/%m/%Y"))
    return http.HTTPStatus.FORBIDDEN


@app.route('/receptionist/tra-cuu', methods=['GET'])
@login_required
def receptionist_phieu_dieu_tri_search():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
        return render_template('receptionist/receptionist_search_pdt.html')
    return http.HTTPStatus.FORBIDDEN


@app.route('/receptionist/patients/register', methods=['GET'])
@login_required
def register_patient_view():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
        page = request.args.get('page', 1, type=int)
        ho_ten = request.args.get('ho_ten')
        so_dien_thoai = request.args.get('so_dien_thoai')
        profiles = None
        profile_selected_id = request.args.get('profile_selected_id')
        selected_profile = None
        if profile_selected_id:
            selected_profile = user_dao.get_user_by_id(profile_selected_id)

        if so_dien_thoai or ho_ten:
            profiles = receptionistDao.get_nguoi_dung_by_sdt_hoten(so_dien_thoai, ho_ten, UserRole.USER, page=page)
        return render_template('receptionist/receptionist_manage.html', profiles=profiles,
                               selected_profile=selected_profile)
    return http.HTTPStatus.FORBIDDEN


@app.route('/receptionist/patients/register', methods=['POST'])
@login_required
def create_patient_profile():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
        try:
            ho_ten = request.form.get('ho_ten')
            so_dien_thoai = request.form.get('so_dien_thoai')
            vn_phone_pattern = r"^0\d{9}$"
            if not ho_ten or not so_dien_thoai:
                flash('Vui lòng nhập đầy đủ Họ tên và Số điện thoại!', 'danger')
                return redirect(url_for('register_patient_view'))
            if not re.match(vn_phone_pattern, so_dien_thoai):
                flash('Số điện thoại không hợp lệ! (Phải là 10 số, bắt đầu bằng 0)', 'warning')
                return redirect(url_for('register_patient_view'))
            if any(char.isdigit() for char in ho_ten):
                flash('Họ tên không được chứa chữ số!', 'warning')
                return redirect(url_for('register_patient_view'))
            dia_chi = request.form.get('dia_chi')
            gioi_tinh = GioiTinh(request.form.get('gioi_tinh'))
            user_id_raw = request.form.get('user_id')
            user_id = None

            if user_id_raw and user_id_raw.split():
                user_id = int(user_id_raw)

            if receptionistDao.get_ho_so_benh_nhan_by_hoten_sodienthoai(ho_ten, so_dien_thoai):
                flash(f'Hồ sơ của "{ho_ten}" ({so_dien_thoai}) đã tồn tại!', 'warning')
            else:
                new_profile = HoSoBenhNhan(ho_ten=ho_ten, so_dien_thoai=so_dien_thoai, dia_chi=dia_chi,
                                           gioi_tinh=gioi_tinh,
                                           nguoi_dung_id=user_id)
                db.session.add(new_profile)
                db.session.commit()
        except Exception as e:
            db.session.rollback()

        return redirect(url_for('register_patient_view'))

    return http.HTTPStatus.NOT_FOUND
