import http
import os

from DentFlowApp import app, db
from flask import render_template, request, jsonify, flash, redirect
from flask_login import current_user, login_required

from DentFlowApp.dao.phieu_dieu_tri_dao import get_ds_thuoc_by_phieu_dieu_tri
from DentFlowApp.dao.receptionistDao import get_phieu_dieu_tri_by_id
from DentFlowApp.dao.thungan_dao import get_phieu_dieu_tri_chua_thanh_toan, \
    get_ds_phieu_dieu_tri_da_thanh_toan
from DentFlowApp.decorators import cashier_required
from DentFlowApp.models import UserRole, TrangThaiThanhToan, HoaDon, PhuongThucThanhToan, LoThuoc
import datetime


@app.route('/cashier', methods=['GET'])
@cashier_required
def cashier_view():
    page = request.args.get('page', 1, type=int)
    page_history = request.args.get('page_tt', 1, type=int)
    page_size = app.config['PAGE_SIZE']
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    active_tab = request.args.get('tab')
    ds_phieu_dieu_tri_chua_thanh_toan = get_phieu_dieu_tri_chua_thanh_toan(page=page,
                                                                           PAGE_SIZE=page_size)  # pagination
    ds_phieu_dieu_tri_da_thanh_toan = get_ds_phieu_dieu_tri_da_thanh_toan(page=page_history, PAGE_SIZE=page_size)
    # tong_tien = get_tong_tien_by_phieu_dieu_tri(phieu_dieu_tri)
    return render_template('cashier/trang_thungan.html', thungan=True, pagination=ds_phieu_dieu_tri_chua_thanh_toan,
                           active_tab=active_tab,
                           pagination_tt=ds_phieu_dieu_tri_da_thanh_toan, time_now=now)


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
        for ct in phieu_dieu_tri.chi_tiet_don_thuoc:
            so_luong_can = ct.so_luong
            thuoc_id = ct.thuoc_id
            lo_thuocs = LoThuoc.query.filter(
                LoThuoc.thuoc_id == thuoc_id,
                LoThuoc.so_luong > 0
            ).order_by(LoThuoc.han_dung_ngay.asc()).all()

            tong_ton_kho = sum(lo.so_luong for lo in lo_thuocs)

            if tong_ton_kho < so_luong_can:
                flash(f"Kho không đủ thuốc: {ct.thuoc.ten_thuoc} (Cần: {so_luong_can}, Còn: {tong_ton_kho})", 'danger')

            # Thực hiện trừ dần
            for lo in lo_thuocs:
                if so_luong_can <= 0:
                    break

                if lo.so_luong >= so_luong_can:
                    lo.so_luong -= so_luong_can
                    so_luong_can = 0
                else:
                    so_luong_can -= lo.so_luong
                    lo.so_luong = 0
        tong_tien = request.form.get('tong-tien-thu')
        phuong_thuc_thanh_toan_selected = request.form.get('phuong_thuc_thanh_toan')
        phuong_thuc_thanh_toan = PhuongThucThanhToan.TIEN_MAT

        if phuong_thuc_thanh_toan_selected == '2':
            phuong_thuc_thanh_toan = PhuongThucThanhToan.CHUYEN_KHOAN_VIETQR
        elif phuong_thuc_thanh_toan_selected == '3':
            phuong_thuc_thanh_toan = PhuongThucThanhToan.CHUYEN_KHOAN_MOMO
        phieu_dieu_tri.trang_thai_thanh_toan = TrangThaiThanhToan.DA_THANH_TOAN
        new_hoa_don = HoaDon(tong_tien=tong_tien, phieu_dieu_tri_id=phieu_dieu_tri.id, nhan_vien_id=current_user.id,
                             phuong_thuc_thanh_toan=phuong_thuc_thanh_toan)
        db.session.add(new_hoa_don)
        db.session.commit()
        flash(f"Xác lập thanh toán hóa đơn thành công cho mã phiếu {phieu_dieu_tri.id}", 'success')
        return redirect('/cashier')
    except Exception as ex:
        db.session.rollback()
        flash(f"Lỗi thanh toán: {ex}", 'danger')
        return jsonify({'status': 'error', 'msg': str(ex)})
