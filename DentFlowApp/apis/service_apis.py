from DentFlowApp import app
from flask import request, jsonify
from flask_login import current_user, login_required
from DentFlowApp.dao import receptionistDao, dichvu_dao
from DentFlowApp.dao.receptionistDao import get_phieu_dieu_tri_by_id
from DentFlowApp.dao.thungan_dao import get_ds_phieu_dieu_tri_da_thanh_toan, get_phieu_dieu_tri_da_thanh_toan_by_id
from DentFlowApp.models import UserRole


@app.route('/api/phieu-dieu-tri/search', methods=['GET'])
@login_required
def search_treatment_slips():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.CASHIER:
        receiver_code = request.args.get('id')
        results = []
        if receiver_code:
            phieu_dieu_tri = get_phieu_dieu_tri_by_id(receiver_code)
            if phieu_dieu_tri:
                results.append({
                    'id': phieu_dieu_tri.id,
                    'ho_so_benh_nhan.ho_ten': phieu_dieu_tri.ho_so_benh_nhan.ho_ten,
                    'dich_vu.ten_dich_vu': phieu_dieu_tri.chi_tiet_dich_vu[0].dich_vu.ten_dich_vu,
                    'dich_vu.don_gia': phieu_dieu_tri.chi_tiet_dich_vu[0].don_gia,
                    'trang_thai': phieu_dieu_tri.trang_thai_thanh_toan.name,
                    'ghi_chu': phieu_dieu_tri.ghi_chu,
                })

        return jsonify({
            'status': 'success',
            'data': results
        })

    return jsonify({'status': 'error', 'message': 'Không có quyền truy cập'}), 403

@app.route('/api/dich-vu', methods=['GET'])
def get_danh_sach_dich_vu():
    try:
        page = request.args.get('page')
        if page:
            dich_vu = dichvu_dao.get_dich_vu(page)
        else:
            print('work')
            dich_vu = dichvu_dao.get_dich_vu()
        print('work2')
        data = [{
            'id': dv.id,
            'ten_dich_vu': dv.ten_dich_vu,
            'don_gia': dv.don_gia
        } for dv in dich_vu]
        return jsonify(data)
    except Exception as e:
        return jsonify([]), 500

