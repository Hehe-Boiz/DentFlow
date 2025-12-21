from flask import jsonify, request
from DentFlowApp import app
from DentFlowApp.dao import ho_so_benh_nhan_dao


@app.route('/api/profile/<int:id>')
def get_profile_detail(id):
    ho_so = ho_so_benh_nhan_dao.get_ho_so_theo_id(id)
    return jsonify(ho_so.to_dict())

@app.route('/api/profile')
def get_profiles():
    try:
        kw = request.args.get('kw').strip()
        page = int(request.args.get('page', 1))
        ho_so = ho_so_benh_nhan_dao.get_ho_so(page=page,kw=kw)
        data = []
        for hs in ho_so:
            data.append({
                'id': hs.id,
                'ho_ten': hs.ho_ten,
                'so_dien_thoai': hs.so_dien_thoai if hs.so_dien_thoai else "",
                'dia_chi': hs.dia_chi if hs.dia_chi else "",
                'email': hs.email if hs.email else "" ,
                'nam_sinh': hs.ngay_sinh.year if hs.ngay_sinh else "",
                'CCCD': hs.CCCD if hs.CCCD else ""
            })
        page_size = app.config['PAGE_SIZE']
        has_next = len(data) == page_size
        return jsonify({
            'status': 'success',
            'data': data,
            'has_next': has_next,
            'next_page': page + 1
        })
    except Exception as ex:
        return jsonify({
            'status': 'error',
            'msg': str(ex)
        }), 500