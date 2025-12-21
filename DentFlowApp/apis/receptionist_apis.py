import http
import math
import re
from DentFlowApp import app, db
from flask import request, redirect, render_template, url_for, flash, session, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from DentFlowApp.dao import receptionistDao, user_dao, lich_hen_dao,ho_so_benh_nhan_dao
from DentFlowApp.models import UserRole, GioiTinh, HoSoBenhNhan, TrangThaiLichHen
from DentFlowApp.utils import validate_thong_tin_benh_nhan

@app.route('/receptionist', methods=['GET'])
@login_required
def receptionist():
    flash('none')
    if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
        active_tab = request.args.get('tab', 'schedule')
        session['stats_cards'] = {
            "Lịch hôm nay": 0,
            "Chờ xác nhận": 0,
            "Tổng lịch hẹn": 0
        }
        lich_hen = None
        ho_so = None
        if active_tab == 'schedule':
            lich_hen = lich_hen_dao.get_lich_hen(page=int(request.args.get('page', 1)))
        if active_tab == 'profile':
            ho_so = ho_so_benh_nhan_dao.get_ho_so(page=int(request.args.get('page', 1)))
        return render_template('receptionist/receptionist.html',
                               active_tab=active_tab,
                               letan=True,
                               lich_hen=lich_hen,
                               ho_so=ho_so,
                               pages=math.ceil(lich_hen_dao.get_tong_lich_hen() / app.config['PAGE_SIZE']),
                               now=datetime.now().strftime("%Y-%m-%d"))
    return http.HTTPStatus.FORBIDDEN

@app.route('/receptionist/tra-cuu', methods=['GET'])
@login_required
def receptionist_phieu_dieu_tri_search():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
        return render_template('receptionist/receptionist_search_pdt.html')
    return http.HTTPStatus.FORBIDDEN
#
#
# @app.route('/receptionist/patients/register', methods=['GET'])
# @login_required
# def register_patient_view():
#     if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
#         page = request.args.get('page', 1, type=int)
#         ho_ten = request.args.get('ho_ten')
#         so_dien_thoai = request.args.get('so_dien_thoai')
#         profiles = None
#         profile_selected_id = request.args.get('profile_selected_id')
#         selected_profile = None
#         if profile_selected_id:
#             selected_profile = user_dao.get_user_by_id(profile_selected_id)
#
#         if so_dien_thoai or ho_ten:
#             profiles = receptionistDao.get_nguoi_dung_by_sdt_hoten(so_dien_thoai, ho_ten, UserRole.USER, page=page)
#         return render_template('receptionist/receptionist_manage.html', profiles=profiles,
#                                selected_profile=selected_profile)
#     return http.HTTPStatus.FORBIDDEN
#
#
# @app.route('/receptionist/patients/register', methods=['POST'])
# @login_required
# def create_patient_profile():
#     if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
#         try:
#             ho_ten = request.form.get('ho_ten')
#             so_dien_thoai = request.form.get('so_dien_thoai')
#             vn_phone_pattern = r"^0\d{9}$"
#             if not ho_ten or not so_dien_thoai:
#                 flash('Vui lòng nhập đầy đủ Họ tên và Số điện thoại!', 'danger')
#                 return redirect(url_for('register_patient_view'))
#             if not re.match(vn_phone_pattern, so_dien_thoai):
#                 flash('Số điện thoại không hợp lệ! (Phải là 10 số, bắt đầu bằng 0)', 'warning')
#                 return redirect(url_for('register_patient_view'))
#             if any(char.isdigit() for char in ho_ten):
#                 flash('Họ tên không được chứa chữ số!', 'warning')
#                 return redirect(url_for('register_patient_view'))
#             dia_chi = request.form.get('dia_chi')
#             gioi_tinh = GioiTinh(request.form.get('gioi_tinh'))
#             user_id_raw = request.form.get('user_id')
#             user_id = None
#
#             if user_id_raw and user_id_raw.split():
#                 user_id = int(user_id_raw)
#
#             if receptionistDao.get_ho_so_benh_nhan_by_hoten_sodienthoai(ho_ten, so_dien_thoai):
#                 flash(f'Hồ sơ của "{ho_ten}" ({so_dien_thoai}) đã tồn tại!', 'warning')
#             else:
#                 new_profile = HoSoBenhNhan(ho_ten=ho_ten, so_dien_thoai=so_dien_thoai, dia_chi=dia_chi,
#                                            gioi_tinh=gioi_tinh,
#                                            nguoi_dung_id=user_id)
#                 db.session.add(new_profile)
#                 db.session.commit()
#         except Exception as e:
#             db.session.rollback()
#
#         return redirect(url_for('register_patient_view'))
#
#     return http.HTTPStatus.NOT_FOUND
@app.route('/receptionist/add-appointment', methods=['POST'])
@login_required
def add_appointment():
    if current_user.vai_tro == UserRole.RECEPTIONIST:
        try:
            ho_so_id = request.form.get('ho_so_id')
            bac_si_id = request.form.get('bac_si_id')
            ngay_dat = request.form.get('ngay_dat')
            gio_kham = request.form.get('gio_kham')
            dich_vu_id = request.form.get('dich_vu_id')
            ghi_chu = request.form.get('ghi_chu')
            lich_hen_dao.add_lich_hen(
                ho_so_benh_nhan_id=ho_so_id,
                ngay_dat=ngay_dat,
                gio_kham=gio_kham,
                bac_si_id=bac_si_id,
                dich_vu_id=dich_vu_id,
                ghi_chu=ghi_chu
            )
            flash("Tạo lịch thành công", 'success')
            print('success')
            return redirect('/receptionist')
        except Exception as ex:
            print('loi')
    return redirect('/receptionist')


@app.route('/receptionist/appointment/<int:lich_hen_id>', methods=['PUT'])
def accept_booked_appointment(lich_hen_id):
    if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
        try:
            lich_hen = lich_hen_dao.get_lich_hen_theo_id(lich_hen_id)
            lich_hen.trang_thai = TrangThaiLichHen.CHO_KHAM
            print(lich_hen)
            db.session.commit()
            return jsonify({'status': 'success', 'msg': 'Xác nhận thành công'})
        except Exception as ex:
            db.session.rollback()
            return jsonify({'status': 'error', 'msg': str(ex)})

@app.route('/receptionist/appointment/<int:lich_hen_id>', methods=['DELETE'])
def delete_booked_appointment(lich_hen_id):
    if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
        try:
            if lich_hen_dao.del_lich_hen(lich_hen_id):
                return jsonify({'status': 'success','msg': 'Xóa thành công'})
            else:
                return jsonify({'status': 'error', 'msg': 'Không có lịch hẹn cần xóa'})
        except Exception as ex:
            return jsonify({'status': 'error', 'msg': str(ex)})

@app.route('/receptionist/update-profiles/<int:ho_so_id>', methods=['POST'])
@login_required
def update_profile_receptionist_page(ho_so_id):
    if current_user.vai_tro == UserRole.RECEPTIONIST:
        try:
            ngay_sinh = request.form.get('ngay_sinh')
            print(ngay_sinh)
            if ngay_sinh != "":
                ngay_sinh = datetime.strptime(ngay_sinh, '%Y-%m-%d')
            else:
                print('test')
                ngay_sinh = None
            gioi_tinh = request.form.get('gioi_tinh')
            if gioi_tinh == 'NAM':
                gioi_tinh = GioiTinh.NAM
            elif gioi_tinh == 'NU':
                gioi_tinh = GioiTinh.NU
            else:
                gioi_tinh = GioiTinh.KHAC
            ho_ten = request.form.get('ho_ten')
            so_dien_thoai = request.form.get('so_dien_thoai')
            email = request.form.get('email')
            CCCD = request.form.get('CCCD')
            dia_chi = request.form.get('dia_chi')
            is_valid, error_msg = validate_thong_tin_benh_nhan(ho_ten, so_dien_thoai, email)
            if not is_valid:
                return jsonify({
                    'status': 'error',
                    'err_msg': 'err_msg'
                })
            if ho_so_benh_nhan_dao.update_ho_so(
                ho_so_id=ho_so_id,
                ho_ten=ho_ten,
                so_dien_thoai=so_dien_thoai,
                dia_chi=dia_chi,
                email=email,
                CCCD=CCCD,
                gioi_tinh=gioi_tinh,
                ngay_sinh=ngay_sinh
            ):
                print(ho_so_benh_nhan_dao.get_ho_so_theo_id(ho_so_id))
                flash('Cập nhật thành công', 'success')
            else:
                print('fail')
                flash('Cập nhật thất bại', 'error')
        except Exception as ex:
            print('Loi')
            flash(str(ex),'error')
    return redirect('/receptionist?tab=profile')

@app.route('/receptionist/create-profiles', methods=['POST'])
@login_required
def create_profile_receptionist_page():
    if current_user.vai_tro == UserRole.RECEPTIONIST:
        try:
            ngay_sinh = request.json.get('ngay_sinh')
            print(ngay_sinh)
            if ngay_sinh != "":
                ngay_sinh = datetime.strptime(ngay_sinh, '%Y-%m-%d')
            else:
                print('test')
                ngay_sinh = None
            gioi_tinh = request.json.get('gioi_tinh')
            if gioi_tinh == 'NAM':
                print('work')
                gioi_tinh = GioiTinh.NAM
            elif gioi_tinh == 'NU':
                gioi_tinh = GioiTinh.NU
            else:
                gioi_tinh = GioiTinh.KHAC
            ho_ten = request.json.get('ho_ten')
            so_dien_thoai = request.json.get('so_dien_thoai')
            email = request.json.get('email')
            CCCD = request.json.get('CCCD')
            dia_chi = request.json.get('dia_chi')
            print("good")
            is_valid, error_msg = validate_thong_tin_benh_nhan(ho_ten=ho_ten, sdt=so_dien_thoai, email=email)
            if not is_valid:
                print('work')
                return jsonify({
                    'status': 'error',
                    'msg': f'{error_msg}'
                })
            ho_so_benh_nhan_dao.add_ho_so(
                    ho_ten=ho_ten,
                    so_dien_thoai=so_dien_thoai,
                    dia_chi=dia_chi,
                    email=email,
                    CCCD=CCCD,
                    gioi_tinh=gioi_tinh,
                    ngay_sinh=ngay_sinh
            )
            flash('Tạo thành công', 'success')
            return jsonify({
                'status': 'success',
                'msg': 'Tạo thành công'
            })
        except Exception as ex:
            print('Loi')
            return jsonify({
                'status': 'error',
                'msg': 'Co loi xay ra'
            })
    return redirect('/receptionist')

