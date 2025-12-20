from DentFlowApp import app, db
from flask import request, redirect, render_template, session, jsonify
from flask_login import current_user, login_required
from DentFlowApp import utils
from DentFlowApp.dao import lich_hen_dao, dichvu_dao, bacsi_dao, thuoc_dao, phieu_dieu_tri_dao
from datetime import datetime

now = datetime.now()
formatted = now.strftime("%d/%m/%Y")


# @app.route('/treatment')
# def treatment_view():
#     bacsi_id = current_user.bac_si.ma_bac_si
#     patients = lich_hen_dao.get_lich_hen_theo_bac_si_today_date_time(bacsi_id)
#     services = dichvu_dao.get_services()
#     count_lich_kham = len(patients)
#     count_lich_da_kham = len(lich_hen_dao.get_lich_hen_da_kham_theo_bac_si())
#     count_lich_cho_kham = max(count_lich_kham - count_lich_da_kham, 0)
#     bacsi = bacsi_dao.get_doctors_by_id(bacsi_id)
#     count_tong_lich_hen = len(lich_hen_dao.get_tong_lich_hen_theo_bac_si())
#     session['stats_cards'] = {
#         "Lịch hôm nay": count_lich_kham,
#         "Chờ khám": count_lich_cho_kham,
#         "Hoàn thành": count_lich_da_kham,
#         "Tổng lịch hẹn": count_tong_lich_hen
#     }
#     print(patients)
#     return render_template(
#         'treatments/treatment.html',
#         patients=patients,
#         services=services,
#         count_lich_kham=count_lich_kham,
#         count_lich_da_kham=count_lich_da_kham,
#         count_lich_cho_kham=count_lich_cho_kham,
#         count_tong_lich_hen=count_tong_lich_hen,
#         bacsi=bacsi,
#         now=formatted
#     )

@app.route('/treatment')
def treatment_view():
    bacsi_id = current_user.bac_si.ma_bac_si
    patients = lich_hen_dao.get_lich_hen_theo_bac_si_today_time(bacsi_id)
    print(len(patients))
    return render_template("treatments/treatment.html", patients=patients)

@app.get("/treatments/ke-don")
def ke_don_partial():
    thuocs = thuoc_dao.get_thuoc_all()
    return render_template("treatments/ke_don_thuoc.html", thuocs=thuocs)


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


@app.route('/treatment', methods=['POST'])
@login_required
def create_treatment():
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'Không có dữ liệu gửi lên'}), 400
        patient_id = data.get("patient_id")
        chan_doan = data.get("chan_doan", "")
        ghi_chu = data.get("ghi_chu", "")
        services = data.get("services", [])
        medicines = data.get("medicines", [])

        if not patient_id:
            return jsonify({'status': 'error', 'message': 'Chưa chọn bệnh nhân'}), 400

        phieu = phieu_dieu_tri_dao.add_phieu_dieu_tri_flush(
            ghi_chu=ghi_chu,
            chan_doan=chan_doan,
            patient_id=int(patient_id),
            bac_si_id=current_user.bac_si.ma_bac_si,
        )

        for s in services:
            detail = dichvu_dao.add_dich_vu(
                phieu_dieu_tri_id=phieu.id,
                dich_vu_id=int(s['id']),
                don_gia=s['price']
            )

        if len(medicines) > 0:
            don_thuoc = thuoc_dao.add_don_thuoc_add_flush(phieu_dieu_tri_id=phieu.id)

            for m in medicines:

                # Tạo string hướng dẫn: "Sáng - Sau ăn - 3 ngày"
                buoi_uong = m.get('buoi_uong', '').strip()
                thoi_diem = m.get('thoi_diem', '').strip()
                so_ngay = m.get('so_ngay', '').strip()
                ghi_chu = m.get('ghi_chu', '').strip()
                parts = []

                if buoi_uong:
                    parts.append(buoi_uong)

                if thoi_diem:
                    parts.append(thoi_diem)

                if so_ngay:
                    parts.append(f"{so_ngay} ngày")

                hd = " - ".join(parts)

                if ghi_chu:
                    if hd:
                        hd = f"{hd}, {ghi_chu}"
                    else:
                        hd = ghi_chu

                lieu_dung = int(m.get('lieu_dung', 0))
                so_ngay = int(m.get('so_ngay', 0))
                tong_so_luong = lieu_dung * so_ngay

                item = thuoc_dao.add_lieu_thuoc_add_flush(
                    don_thuoc_id=don_thuoc.id,
                    thuoc_id=int(m['id']),
                    so_luong=tong_so_luong,
                    huong_dan=hd
                )
        db.session.commit()
        return jsonify({'status': 'success', 'treatment_id': phieu.id})

    except Exception as e:
        db.session.rollback()  # Hoàn tác nếu lỗi
        print(f"Error creating treatment: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.get("/tabs/today")
# def tabs_today():
#     return render_template("treatments/tab_schedule_today.html")
#
# @app.get("/tabs/work")
# def tabs_work():
#     return render_template("treatments/tab_schedule.html")
#
# @app.get("/tabs/treatment")
# def tabs_treatment():
#     return render_template("treatments/tab_treatment.html")
