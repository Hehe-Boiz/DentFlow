from DentFlowApp import app,db
from flask import request, redirect, render_template, session, jsonify
from flask_login import current_user, login_required
from DentFlowApp import utils
from DentFlowApp.dao import lich_hen_dao, dichvu_dao, bacsi_dao, thuoc_dao
from datetime import datetime
now = datetime.now()
formatted = now.strftime("%d/%m/%Y")
@app.route('/treatment')
def treatment_view():
    bacsi_id = current_user.bac_si.ma_bac_si
    patients = lich_hen_dao.get_lich_hen_theo_bac_si()
    services = dichvu_dao.get_services()
    count_lich_kham =len(patients)
    count_lich_da_kham = len(lich_hen_dao.get_lich_hen_da_kham_theo_bac_si())
    count_lich_cho_kham = max(count_lich_kham - count_lich_da_kham, 0)
    bacsi = bacsi_dao.get_doctors_by_id(bacsi_id)
    count_tong_lich_hen = len(lich_hen_dao.get_tong_lich_hen_theo_bac_si())
    session['stats_cards'] = {
        "Lịch hôm nay": count_lich_kham,
        "Chờ khám": count_lich_cho_kham,
        "Hoàn thành": count_lich_da_kham,
        "Tổng lịch hẹn": count_tong_lich_hen
    }
    print(patients)
    return  render_template(
        'treatments/treatment.html',
        patients = patients,
        services=services,
        count_lich_kham = count_lich_kham,
        count_lich_da_kham = count_lich_da_kham,
        count_lich_cho_kham = count_lich_cho_kham,
        count_tong_lich_hen = count_tong_lich_hen,
        bacsi = bacsi,
        now = formatted
    )

@app.get("/treatments/ke-don")
def ke_don_partial():
    thuocs = thuoc_dao.get_thuoc_all()
    return render_template("treatments/ke_don_thuoc.html", thuocs = thuocs)

@app.route('/api/thuoc/<int:thuoc_id>/lo-thuoc', methods=['GET'])
@login_required
def get_lo_thuoc(thuoc_id):
    """Lấy tất cả lô thuốc còn hạn của một loại thuốc"""
    try:
        lo_thuocs = thuoc_dao.get_lo_thuoc_by_thuoc_id(thuoc_id)
        result = []
        for lo in lo_thuocs:
            result.append({
                'id': lo.id,
                'so_lo': getattr(lo, 'so_lo', f'Lô {lo.id}'),
                'han_su_dung': lo.han_su_dung.strftime('%d/%m/%Y'),
                'han_su_dung_raw': lo.han_su_dung.strftime('%Y-%m-%d'),
                'so_luong_ton': lo.so_luong,
                'ngay_nhap': lo.ngay_nhap.strftime('%d/%m/%Y')
            })
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/thuoc/<int:thuoc_id>/lo-phu-hop', methods=['POST'])
@login_required
def get_lo_phu_hop(thuoc_id):
    """Tự động chọn lô thuốc phù hợp dựa trên số ngày dùng"""
    try:
        so_ngay = request.json.get('so_ngay_dung', 0)
        # Validate input cơ bản
        if not so_ngay or int(so_ngay) <= 0:
            return jsonify({'status': 'error', 'message': 'Số ngày dùng phải lớn hơn 0'}), 400

        # Gọi Utils để xử lý logic
        success, lo_thuoc, message = utils.ValidationUtils.tim_lo_thuoc_tot_nhat(thuoc_id, so_ngay)

        if success and lo_thuoc:
            result = {
                'id': lo_thuoc.id,
                'so_lo': getattr(lo_thuoc, 'so_lo', f'Lô {lo_thuoc.id}'),
                'han_su_dung': lo_thuoc.han_su_dung.strftime('%d/%m/%Y'),
                'han_su_dung_raw': lo_thuoc.han_su_dung.strftime('%Y-%m-%d'),
                'so_luong_ton': lo_thuoc.so_luong
            }
            return jsonify({'status': 'success', 'data': result, 'message': message})
        else:
            # Trả về warning để frontend hiển thị lỗi (ví dụ: chỉ còn dùng được X ngày)
            return jsonify({
                'status': 'warning',
                'message': message
            }), 200  # Trả về 200 để frontend dễ xử lý logic warning

    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 'message': 'Lỗi server khi tìm thuốc'}), 500

