from flask import request, jsonify
import datetime
from DentFlowApp import app
from DentFlowApp.dao.lichlamviecDao import get_schedules_by_day_by_doctor
from DentFlowApp.models import LichLamViec


@app.route('/api/get-schedules', methods=['post'])
def get_schedules():
    id = request.json.get('id')
    day = request.json.get('day')
    lich_kha_dung = get_schedules_by_day_by_doctor(id=id, day=day)
    print(id, day)
    print(get_schedules_by_day_by_doctor(id=id, day=day))
    lich_tra_ve = {}
    index = 0
    for lich in lich_kha_dung:
        lich_tra_ve[index] = {
            'ma_bac_si': lich.bac_si_id,
            'gio_bat_dau': lich.gio_bat_dau.strftime('%H:%M'),
            'gio_ket_thuc': lich.gio_ket_thuc.strftime('%H:%M'),
            'trang_thai': lich.trang_thai.value
        }
        index += 1
    print(lich_tra_ve)
    return jsonify(lich_tra_ve)