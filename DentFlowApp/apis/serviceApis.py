import http
from DentFlowApp import app
from flask import request, render_template, jsonify
from flask_login import current_user, login_required
from DentFlowApp import utils
from DentFlowApp.dao import receptionistDao
from DentFlowApp.models import UserRole


@app.route('/api/phieu-dieu-tri/search', methods=['GET'])
@login_required
def search_treatment_slips():
    if current_user.is_authenticated and (
            current_user.vai_tro == UserRole.RECEPTIONIST or current_user.vai_tro == UserRole.CASHIER):

        receiver_code = request.args.get('code')
        results = []
        if receiver_code:
            phieu_dieu_tri = receptionistDao.get_phieu_dieu_tri_by_maso(receiver_code)
            if phieu_dieu_tri:
                results.append({
                    'id': phieu_dieu_tri.id,
                    'ho_so_benh_nhan.ho_ten': phieu_dieu_tri.ho_so_benh_nhan.ho_ten,
                    'dich_vu.ten_dich_vu': phieu_dieu_tri.dich_vu.ten_dich_vu,
                    'dich_vu.don_gia': phieu_dieu_tri.dich_vu.don_gia,
                    'ghi_chu': phieu_dieu_tri.ghi_chu,
                })

        return jsonify({
            'status': 'success',
            'data': results
        })
    return jsonify({'status': 'error', 'message': 'Không có quyền truy cập'}), 403
