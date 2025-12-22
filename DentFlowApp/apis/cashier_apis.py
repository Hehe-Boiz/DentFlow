import http
from DentFlowApp import app, db
from flask import render_template, request, jsonify
from flask_login import current_user, login_required
from DentFlowApp.dao.receptionistDao import get_phieu_dieu_tri_by_id
from DentFlowApp.dao.thungan_dao import get_phieu_dieu_tri_chua_thanh_toan, \
    get_ds_phieu_dieu_tri_da_thanh_toan
from DentFlowApp.models import UserRole, TrangThaiThanhToan, HoaDon, PhuongThucThanhToan


@app.route('/cashier', methods=['GET'])
@login_required
def cashier_view():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.CASHIER:
        page = request.args.get('page', 1, type=int)
        page_size = app.config['PAGE_SIZE']
        active_tab = request.args.get('tab')
        ds_phieu_dieu_tri_chua_thanh_toan = get_phieu_dieu_tri_chua_thanh_toan(page=page,
                                                                               PAGE_SIZE=page_size)  # pagination
        ds_phieu_dieu_tri_da_thanh_toan = get_ds_phieu_dieu_tri_da_thanh_toan(page=page, PAGE_SIZE=page_size)
        # tong_tien = get_tong_tien_by_phieu_dieu_tri(phieu_dieu_tri)
        return render_template('cashier/cashier.html', thungan=True, pagination=ds_phieu_dieu_tri_chua_thanh_toan,
                               active_tab=active_tab,
                               pagination_tt=ds_phieu_dieu_tri_da_thanh_toan)
    return http.HTTPStatus.FORBIDDEN


@app.route('/cashier/tra-cuu', methods=['GET'])
@login_required
def cashier_phieu_dieu_tri_search():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.CASHIER:
        return render_template('cashier/cashier_search_pdt.html')
    return http.HTTPStatus.FORBIDDEN


@app.route('/cashier/thanh-toan/<int:id>', methods=['GET'])
@login_required
def cashier_thanh_toan(id):
    if current_user.is_authenticated and current_user.vai_tro == UserRole.CASHIER:
        phieu_dieu_tri = get_phieu_dieu_tri_by_id(id)
        return render_template('cashier/thanh_toan.html', phieu_dieu_tri=phieu_dieu_tri)
    return http.HTTPStatus.FORBIDDEN


@app.route('/cashier/chua-thanh/<int:id>', methods=['POST'])
@login_required
def cashier_xac_nhan_thanh_toan(id):
    if current_user.is_authenticated and current_user.vai_tro == UserRole.CASHIER:
        try:
            phieu_dieu_tri = get_phieu_dieu_tri_by_id(id)
            tong_tien = request.form.get('tong-tien-thu')
            phuong_thuc_thanh_toan_selected = request.form.get('phuong_thuc_thanh_toan')
            phuong_thuc_thanh_toan = PhuongThucThanhToan.TIEN_MAT
            if phuong_thuc_thanh_toan_selected == '2':
                phuong_thuc_thanh_toan = PhuongThucThanhToan.CHUYEN_KHOAN_VIETQR
            elif PhuongThucThanhToan.TIEN_MAT == '3':
                phuong_thuc_thanh_toan = PhuongThucThanhToan.CHUYEN_KHOAN_MOMO
            phieu_dieu_tri.trang_thai_thanh_toan = TrangThaiThanhToan.DA_THANH_TOAN
            new_hoa_don = HoaDon(tong_tien=tong_tien, phieu_dieu_tri_id=phieu_dieu_tri.id, nhan_vien_id=current_user.id,
                                 phuong_thuc_thanh_toan=phuong_thuc_thanh_toan)
            db.session.add(new_hoa_don)
            db.session.commit()
            return jsonify({'status': 'success', 'msg': 'Tạo hóa đơn thành công'})
        except Exception as ex:
            return jsonify({'status': 'error', 'msg': str(ex)})
    return http.HTTPStatus.FORBIDDEN
