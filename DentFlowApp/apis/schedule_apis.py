
from flask import request, jsonify
from datetime import datetime,timedelta
from DentFlowApp import app
from DentFlowApp.dao.lichlamviec_dao import get_lich_san_sang_theo_ngay_theo_bac_si
from DentFlowApp.dao.lich_hen_dao import get_lich_hen_theo_ngay_theo_bac_si


@app.route('/api/lay-thoi-gian-trong', methods=['POST'])
def get_available_slots():
    try:
        data = request.json
        bac_si_id = data.get('id')
        ngay = data.get('day')

        lich_kha_dung = get_lich_san_sang_theo_ngay_theo_bac_si(ngay=ngay,bac_si_id=bac_si_id)
        lich_hen_da_dat = get_lich_hen_theo_ngay_theo_bac_si(ngay=ngay, bac_si_id=bac_si_id)

        print(lich_hen_da_dat)
        thoi_gian_da_dat = [ lh.gio_kham.strftime('%H:%M') for lh in lich_hen_da_dat ]
        thoi_gian_trong = []
        if len(thoi_gian_da_dat) >= 5:
            return jsonify({'status': 'success', 'data': thoi_gian_trong}), 200
        thoi_gian_hien_co = {}

        index = 0
        for lich in lich_kha_dung:
            thoi_gian_hien_co[index] =  {
                'thoi_gian_bat_dau': lich.gio_bat_dau.strftime('%H:%M'),
                'thoi_gian_ket_thuc': lich.gio_ket_thuc.strftime('%H:%M'),
            }
            index += 1

        print(thoi_gian_hien_co)
        hom_nay = datetime.now()
        ngay_hom_nay = hom_nay.strftime("%Y-%m-%d")
        thoi_gian_hom_nay = hom_nay.strftime("%H:%M")
        phut_hom_nay = hom_nay.minute
        gio_hom_nay = hom_nay.hour
        if phut_hom_nay <= 30:
            phut_hom_nay = 30
        if phut_hom_nay > 30:
            phut_hom_nay = 0
            gio_hom_nay += 1
        thoi_gian_hom_nay = datetime(hom_nay.year,hom_nay.month,hom_nay.day,gio_hom_nay,phut_hom_nay,hom_nay.second).strftime("%H:%M")
        thoi_gian_hom_nay_formatted = datetime.strptime(str(thoi_gian_hom_nay), "%H:%M")
        for index, thoi_gian in thoi_gian_hien_co.items():
            thoi_gian_hien_tai = datetime.strptime(str(thoi_gian_hien_co[index]['thoi_gian_bat_dau']), "%H:%M")
            if ngay == ngay_hom_nay:
                if thoi_gian_hien_tai < thoi_gian_hom_nay_formatted:
                    thoi_gian_hien_tai = thoi_gian_hom_nay_formatted
            thoi_gian_ket_thuc = datetime.strptime(str(thoi_gian_hien_co[index]['thoi_gian_ket_thuc']), "%H:%M")
            while thoi_gian_hien_tai < thoi_gian_ket_thuc:
                tg_hien_tai = thoi_gian_hien_tai.strftime('%H:%M')
                if tg_hien_tai not in thoi_gian_da_dat:
                    thoi_gian_trong.append(tg_hien_tai)
                thoi_gian_hien_tai += timedelta(minutes=30)
        print(thoi_gian_da_dat)
        print(thoi_gian_trong)
        return jsonify({'status':'success', 'data': thoi_gian_trong}), 200
    except Exception as ex:
        return jsonify({'status': 'error', 'msg': 'err'}),500
