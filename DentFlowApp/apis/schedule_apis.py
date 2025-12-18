from xml.dom.expatbuilder import theDOMImplementation

from flask import request, jsonify
from datetime import datetime,timedelta
from DentFlowApp import app
from DentFlowApp.dao.lichlamviec_dao import get_schedules_is_ready_by_day_by_doctor
from DentFlowApp.dao.lichhen_dao import get_appointment_by_day_by_doctor
from DentFlowApp.models import LichLamViec


@app.route('/api/get-schedules', methods=['post'])
def get_schedules():
    bac_si_id = request.json.get('id')
    ngay = request.json.get('day')
    lich_kha_dung = get_schedules_is_ready_by_day_by_doctor(bac_si_id=bac_si_id, ngay=ngay)
    print(bac_si_id, ngay)
    print(get_schedules_is_ready_by_day_by_doctor(bac_si_id=bac_si_id, ngay=ngay))
    lich_tra_ve = {}
    index = 0
    for lich in lich_kha_dung:
        lich_tra_ve[index] = {
            'ma_bac_si': lich.bac_si_id,
            'ngay_lam': lich.ngay_lam.strftime('%d/%m/%Y'),
            'gio_bat_dau': lich.gio_bat_dau.strftime('%H:%M'),
            'gio_ket_thuc': lich.gio_ket_thuc.strftime('%H:%M'),
            'trang_thai': lich.trang_thai.value
        }
        index += 1
    print(lich_tra_ve)
    return jsonify(lich_tra_ve)

@app.route('/api/get-available-time-slots', methods=['POST'])
def get_available_slots():
    data = request.json
    bac_si_id = data.get('id')
    ngay = data.get('day')

    # 1. Tìm Lịch Làm Việc của bác sĩ trong ngày đó
    # (Code này dựa trên model LichLamViec của bạn)
    lich_kha_dung = get_schedules_is_ready_by_day_by_doctor(ngay=ngay,bac_si_id=bac_si_id)
    lich_hen_da_dat = get_appointment_by_day_by_doctor(ngay=ngay, bac_si_id=bac_si_id)

    print(lich_hen_da_dat)
    thoi_gian_da_dat = [ lh.gio_kham.strftime('%H:%M') for lh in lich_hen_da_dat ]

    thoi_gian_trong = []

    thoi_gian_hien_co = {}
    # thoi_gian_bat_dau = []
    # thoi_gian_ket_thuc = []
    index = 0
    for lich in lich_kha_dung:
        thoi_gian_hien_co[index] =  {
            'thoi_gian_bat_dau': lich.gio_bat_dau.strftime('%H:%M'),
            'thoi_gian_ket_thuc': lich.gio_ket_thuc.strftime('%H:%M'),
        }
        index += 1
        # thoi_gian_bat_dau.append(lich.gio_bat_dau.strftime('%H:%M'))
        # thoi_gian_ket_thuc.append(lich.gio_ket_thuc.strftime('%H:%M'))


    for index, thoi_gian in thoi_gian_hien_co.items():
        thoi_gian_hien_tai = datetime.strptime(str(thoi_gian_hien_co[index]['thoi_gian_bat_dau']), "%H:%M")
        thoi_gian_ket_thuc = datetime.strptime(str(thoi_gian_hien_co[index]['thoi_gian_ket_thuc']), "%H:%M")
        while thoi_gian_hien_tai < thoi_gian_ket_thuc:
            tg_hien_tai = thoi_gian_hien_tai.strftime('%H:%M')
            if tg_hien_tai not in thoi_gian_da_dat:
                thoi_gian_trong.append(tg_hien_tai)
            thoi_gian_hien_tai += timedelta(minutes=30)
    print(thoi_gian_da_dat)
    print(thoi_gian_trong)
    return jsonify(thoi_gian_trong)