from flask import request, jsonify
from DentFlowApp import app
from DentFlowApp.dao import bacsi_dao
@app.route('/api/bac-si', methods=['GET'])
def get_danh_sach_bac_si():
    try:
        trang_thai = request.args.get('trang_thai')
        if trang_thai and trang_thai == 'san_sang':
            print('hd')
            bac_si = bacsi_dao.get_doctors_is_ready()
        else:
            bac_si = bacsi_dao.get_doctors()
        if bac_si:
            data = [{
                'ma_bac_si': b.ma_bac_si,
                'ho_ten': b.ho_ten,
                'so_dien_thoai': b.so_dien_thoai,
                'loai_bac_si': b.loai_bac_si.value
            } for b in bac_si]
            return jsonify(data)
        else:
            return jsonify([]), 500
    except Exception as e:
        return jsonify([]), 500
