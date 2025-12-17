import http

from sqlalchemy.testing import db_spec

from DentFlowApp import app, db
from flask import request, redirect, render_template, url_for
from flask_login import current_user, login_required
from DentFlowApp import utils
from DentFlowApp.dao import receptionistDao, userDao
from DentFlowApp.models import UserRole, GioiTinh, HoSoBenhNhan


@app.route('/receptionist/phieu-dieu-tri/search', methods=['GET'])
@login_required
def search_treatment_slips():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
        can_do = utils.user_can_do()
        receiver_code = request.args.get('code')
        phieu_dieu_tri = None
        if receiver_code:
            phieu_dieu_tri = receptionistDao.get_phieu_dieu_tri_by_maso(receiver_code)

        return render_template('phieu_dieu_tri_search_service.html', can_do=can_do, phieu_dieu_tri=phieu_dieu_tri)
    return http.HTTPStatus.NOT_FOUND


@app.route('/receptionist/patients/register', methods=['GET'])
@login_required
def register_patient_view():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
        can_do = utils.user_can_do()
        page = request.args.get('page', 1, type=int)
        ho_ten = request.args.get('ho_ten')
        so_dien_thoai = request.args.get('so_dien_thoai')
        profiles = None
        profile_selected_id = request.args.get('profile_selected_id')
        selected_profile = None
        if profile_selected_id:
            selected_profile = userDao.get_user_by_id(profile_selected_id)

        if so_dien_thoai or ho_ten:
            profiles = receptionistDao.get_profile_users_by_sdt_hoten(so_dien_thoai, ho_ten, UserRole.USER, page=page)
        return render_template('user_registration_service.html', can_do=can_do, profiles=profiles,
                               selected_profile=selected_profile)
    return http.HTTPStatus.NOT_FOUND


@app.route('/receptionist/patients/register', methods=['POST'])
@login_required
def create_patient_profile():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
        try:
            ho_ten = request.form.get('ho_ten')
            so_dien_thoai = request.form.get('so_dien_thoai')
            dia_chi = request.form.get('dia_chi')
            gioi_tinh = GioiTinh(request.form.get('gioi_tinh'))
            user_id_raw = request.form.get('user_id')
            user_id = None
            if user_id_raw and user_id_raw.split():
                user_id = int(user_id_raw)

            new_profile = HoSoBenhNhan(ho_ten=ho_ten, so_dien_thoai=so_dien_thoai, dia_chi=dia_chi, gioi_tinh=gioi_tinh,
                                       nguoi_dung_id=user_id)
            db.session.add(new_profile)
            db.session.commit()
        except Exception as e:
            db.session.rollback()

        return redirect(url_for('register_patient_view'))

    return http.HTTPStatus.NOT_FOUND
