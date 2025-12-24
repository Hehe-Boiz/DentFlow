from datetime import datetime

from flask import jsonify, request, flash, redirect
from flask_login import current_user, login_required

from DentFlowApp import app
from DentFlowApp.dao import ho_so_benh_nhan_dao
from DentFlowApp.models import UserRole, GioiTinh
from DentFlowApp.utils import validate_thong_tin_benh_nhan


@app.route('/api/profile/<int:id>')
def get_profile_detail(id):
    ho_so = ho_so_benh_nhan_dao.get_ho_so_theo_id(id)
    return jsonify(ho_so.to_dict())

@app.route('/api/profile')
def get_profiles():
    try:
        kw = request.args.get('kw').strip()
        page = int(request.args.get('page', 1))
        ho_so = ho_so_benh_nhan_dao.get_ho_so(page=page,kw=kw)
        data = []
        for hs in ho_so:
            data.append({
                'id': hs.id,
                'ho_ten': hs.ho_ten,
                'so_dien_thoai': hs.so_dien_thoai if hs.so_dien_thoai else "",
                'dia_chi': hs.dia_chi if hs.dia_chi else "",
                'email': hs.email if hs.email else "" ,
                'nam_sinh': hs.ngay_sinh.year if hs.ngay_sinh else "",
                'CCCD': hs.CCCD if hs.CCCD else ""
            })
        page_size = app.config['PAGE_SIZE']
        has_next = len(data) == page_size
        return jsonify({
            'status': 'success',
            'data': data,
            'has_next': has_next,
            'next_page': page + 1
        })
    except Exception as ex:
        return jsonify({
            'status': 'error',
            'msg': str(ex)
        }), 500

@app.route('/api/create-profiles', methods=['POST'])
@login_required
def create_profile_page():
    nguoi_dung_id = None
    if current_user.vai_tro == UserRole.USER:
        nguoi_dung_id = current_user.id
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
            }), 200
        ho_so_moi = ho_so_benh_nhan_dao.add_ho_so(
                ho_ten=ho_ten,
                so_dien_thoai=so_dien_thoai,
                dia_chi=dia_chi,
                email=email,
                CCCD=CCCD,
                gioi_tinh=gioi_tinh,
                ngay_sinh=ngay_sinh,
                nguoi_dung_id=nguoi_dung_id
        )
        if ho_so_moi:
            flash('Tạo thành công', 'success')
        return jsonify({
            'status': 'success',
            'msg': 'Tạo thành công',
            'data': ho_so_moi.to_dict()
        }), 200
    except Exception as ex:
        print('Loi')
        return jsonify({
            'status': 'error',
            'msg': 'Co loi xay ra'
        }), 500
@app.route('/api/update-profile/<int:ho_so_id>', methods=['POST'])
@login_required
def update_profile_page(ho_so_id):
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
                'err_msg': f'{error_msg}'
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
            flash('Cập nhật thất bại', 'danger')
    except Exception as ex:
        print('Loi')
        flash(str(ex),'error')
    if current_user.vai_tro == UserRole.RECEPTIONIST:
        return redirect('/receptionist?tab=profile')
    else:
        return redirect('/user')