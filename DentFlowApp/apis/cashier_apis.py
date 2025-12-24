import http
import os

from DentFlowApp import app, db
from flask import render_template, request, jsonify
from flask_login import current_user, login_required

from DentFlowApp.dao.phieu_dieu_tri_dao import get_ds_thuoc_by_phieu_dieu_tri
from DentFlowApp.dao.receptionistDao import get_phieu_dieu_tri_by_id
from DentFlowApp.dao.thungan_dao import get_phieu_dieu_tri_chua_thanh_toan, \
    get_ds_phieu_dieu_tri_da_thanh_toan
from DentFlowApp.decorators import cashier_required
from DentFlowApp.models import UserRole, TrangThaiThanhToan, HoaDon, PhuongThucThanhToan


@app.route('/cashier', methods=['GET'])
@cashier_required
def cashier_view():
    page = request.args.get('page', 1, type=int)
    page_size = app.config['PAGE_SIZE']
    active_tab = request.args.get('tab')
    ds_phieu_dieu_tri_chua_thanh_toan = get_phieu_dieu_tri_chua_thanh_toan(page=page,
                                                                           PAGE_SIZE=page_size)  # pagination
    ds_phieu_dieu_tri_da_thanh_toan = get_ds_phieu_dieu_tri_da_thanh_toan(page=page, PAGE_SIZE=page_size)
    # tong_tien = get_tong_tien_by_phieu_dieu_tri(phieu_dieu_tri)
    return render_template('cashier/trang_thungan.html', thungan=True, pagination=ds_phieu_dieu_tri_chua_thanh_toan,
                           active_tab=active_tab,
                           pagination_tt=ds_phieu_dieu_tri_da_thanh_toan)


@app.route('/cashier/tra-cuu', methods=['GET'])
@cashier_required
def cashier_phieu_dieu_tri_search():
    return render_template('cashier/thanh_tim_kiem_pdt.html')


@app.route('/cashier/thanh-toan/<int:id>', methods=['GET'])
@cashier_required
def cashier_thanh_toan(id):
    phieu_dieu_tri = get_phieu_dieu_tri_by_id(id)

    bank_config = {
        'bank_id': os.getenv('BANK_ID'),
        'account_numb': os.getenv('ACCOUNT_NUMB'),
        'template': os.getenv('TEMPLATE'),
    }
    return render_template('cashier/trang_thanh_toan.html', phieu_dieu_tri=phieu_dieu_tri, bank_config=bank_config,
                           )


@app.route('/cashier/thanh-toan/<int:id>', methods=['POST'])
@cashier_required
def cashier_xac_nhan_thanh_toan(id):
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
