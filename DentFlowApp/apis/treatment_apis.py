from DentFlowApp import app, db
from flask import request, redirect, render_template, session, jsonify
from flask_login import current_user, login_required
from DentFlowApp import utils
from DentFlowApp.dao import lich_hen_dao, dichvu_dao, bacsi_dao, thuoc_dao, phieu_dieu_tri_dao, lichlamviec_dao
from datetime import date, datetime, timedelta
from DentFlowApp.decorators import doctor_required
from DentFlowApp.models import TrangThaiLichHen

now = datetime.now()
formatted = now.strftime("%d/%m/%Y")


@app.route('/treatment')
@doctor_required
def treatment_view():
    bacsi_id = current_user.bac_si.ma_bac_si
    patients = lich_hen_dao.get_lich_hen_theo_bac_si_today_date_time(bacsi_id)

    count_lich_kham = len(patients)
    count_lich_da_kham = len(lich_hen_dao.get_lich_hen_da_kham_theo_bac_si_today(bacsi_id))
    count_lich_cho_kham = max(count_lich_kham - count_lich_da_kham, 0)
    bacsi = bacsi_dao.get_doctors_by_id(bacsi_id)
    count_tong_lich_hen = len(lich_hen_dao.get_tong_lich_hen_theo_bac_si(bacsi_id))
    session['stats_cards'] = {
        "Lịch hôm nay": count_lich_kham,
        "Chờ khám": count_lich_cho_kham,
        "Hoàn thành": count_lich_da_kham,
        "Tổng lịch hẹn": count_tong_lich_hen
    }
    print(patients)
    return render_template(
        'treatments/treatment.html',
        count_lich_kham=count_lich_kham,
        count_lich_da_kham=count_lich_da_kham,
        count_lich_cho_kham=count_lich_cho_kham,
        count_tong_lich_hen=count_tong_lich_hen,
        bacsi=bacsi,
        now=formatted
    )


@app.route('/tabs/treatment')
@doctor_required
def create_treatment_view():
    bacsi_id = current_user.bac_si.ma_bac_si
    patients = lich_hen_dao.get_all_lich_hen_by_bac_si(bacsi_id)
    services = dichvu_dao.get_dich_vu()

    context = {
        'patients': patients,
        'services': services
    }
    benh_nhan_id = request.args.get('patient_id', type=int)
    dich_vu_id = request.args.get('dichvu', type=int)
    if benh_nhan_id and dich_vu_id:
        context['selected_patient_id'] = benh_nhan_id
        context['selected_service_id'] = dich_vu_id
    return render_template(
        'treatments/tab_treatment.html',
        **context
    )


@app.route('/tabs/today')
@doctor_required
def lich_hen_today_view():
    bacsi_id = current_user.bac_si.ma_bac_si
    patients = lich_hen_dao.get_lich_hen_theo_bac_si_today_time(bacsi_id)
    print(len(patients))
    return render_template("treatments/tab_schedule_today.html", patients=patients)


@app.get("/treatments/ke-don")
@doctor_required
def ke_don_partial():
    thuocs = thuoc_dao.get_thuoc_all()
    return render_template("treatments/ke_don_thuoc.html", thuocs=thuocs)


@app.route('/treatment/thuoc/<int:thuoc_id>/lo-thuoc', methods=['GET'])
@doctor_required
def get_lo_thuoc(thuoc_id):
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


@app.route('/treatment/thuoc/<int:thuoc_id>/lo-phu-hop', methods=['POST'])
@doctor_required
def get_lo_phu_hop(thuoc_id):

    try:
        so_ngay = request.json.get('so_ngay_dung', 0)
        if not so_ngay or int(so_ngay) <= 0:
            return jsonify({'status': 'error', 'message': 'Số ngày dùng phải lớn hơn 0'}), 400

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
            return jsonify({
                'status': 'warning',
                'message': message
            }), 200

    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 'message': 'Lỗi server khi tìm thuốc'}), 500


@app.route('/treatment', methods=['POST'])
@doctor_required
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
        lich_hen_id = data.get("lich_hen_id", "")

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
        print(lich_hen_id)
        lich_hen = lich_hen_dao.get_lich_hen_theo_id(lich_hen_id)
        lich_hen.trang_thai = TrangThaiLichHen.DA_KHAM
        db.session.commit()
        return jsonify({'status': 'success', 'treatment_id': phieu.id})

    except Exception as e:
        db.session.rollback()
        print(f"Error creating treatment: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/tabs/work")
@doctor_required
def schedule_week():
    day_str = request.args.get("day")
    if day_str:
        base_day = datetime.strptime(day_str, "%Y-%m-%d").date()
    else:
        base_day = date.today()

    monday = utils.get_monday(base_day)
    sunday = utils.get_sunday(base_day)
    days = utils.get_week_dates(monday)

    times = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    system_hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]

    ds_lich = lichlamviec_dao.get_lich_lam_viec_theo_tuan(current_user.bac_si.ma_bac_si, base_day)
    ds_lich_hen = lich_hen_dao.get_tong_lich_hen_in_tuan_by_bac_si(current_user.bac_si.ma_bac_si)
    working_slots = {}
    lich_hen_slots = {}
    for lich in ds_lich:
        start_time_bs = lich.gio_bat_dau
        end_time_bs = lich.gio_ket_thuc

        for h in system_hours:
            slot_start = datetime.strptime(f"{h:02d}:00", "%H:%M").time()
            slot_end = datetime.strptime(f"{h + 1:02d}:00", "%H:%M").time()

            if start_time_bs < slot_end and end_time_bs > slot_start:
                key = f"{lich.ngay_lam.strftime('%Y-%m-%d')}_{h:02d}:00"

                note = ""

                if start_time_bs >= slot_start and start_time_bs < slot_end:
                    if start_time_bs.minute > 0:
                        note = f"Bắt đầu: {start_time_bs.strftime('%H:%M')}"

                elif end_time_bs > slot_start and end_time_bs <= slot_end:
                    if end_time_bs.minute > 0:
                        note = f"Kết thúc: {end_time_bs.strftime('%H:%M')}"

                working_slots[key] = note

    for lh in ds_lich_hen:
        h = lh.gio_kham.hour

        if h in system_hours:
            key = f"{lh.ngay_dat.strftime('%Y-%m-%d')}_{h:02d}:00"
            lich_hen_slots[key] = lich_hen_slots.get(key, 0) + 1

    return render_template("treatments/tab_schedule.html", monday=monday, sunday=sunday, days=days, times=times,
                           working_slots=working_slots, lich_hen_slots=lich_hen_slots)


@app.get("/treatment/lich-hen/slot")
@doctor_required
def api_lich_hen_slot():
    date_str = request.args.get("date")
    time_str = request.args.get("time")

    if not date_str or not time_str:
        return jsonify({"status": "error", "message": "Thiếu date/time"}), 400

    try:
        ngay_dat = datetime.strptime(date_str, "%Y-%m-%d").date()
        gio_h = int(time_str.split(":")[0])
    except Exception:
        return jsonify({"status": "error", "message": "Sai format date/time"}), 400

    bacsi_id = current_user.bac_si.ma_bac_si

    ds = lich_hen_dao.get_lich_hen_by_bac_si_and_slot(bacsi_id, ngay_dat, gio_h)

    items = []
    for lh in ds:
        items.append({
            "id": lh.id,
            "gio_kham": lh.gio_kham.strftime("%H:%M"),
            "trang_thai": lh.trang_thai.name if lh.trang_thai else "",
            "trang_thai_text": lh.trang_thai.value if lh.trang_thai else "",
            "benh_nhan_ho_ten": lh.ho_so_benh_nhan.ho_ten if lh.ho_so_benh_nhan else "",
            "dich_vu_ten": lh.dich_vu.ten_dich_vu if lh.dich_vu else "",
            "ghi_chu": lh.ghi_chu or ""
        })

    return jsonify({"status": "success", "items": items})
