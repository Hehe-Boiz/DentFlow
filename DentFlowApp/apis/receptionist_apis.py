import math
from DentFlowApp import app, db
from flask import request, redirect, render_template, flash, session, jsonify
from datetime import datetime
from DentFlowApp.dao import lich_hen_dao, ho_so_benh_nhan_dao
from DentFlowApp.models import TrangThaiLichHen
from DentFlowApp.decorators import receptionist_required


@app.route('/receptionist', methods=['GET'])
@receptionist_required
def receptionist():
    flash('none')
    active_tab = request.args.get('tab', 'schedule')
    session['stats_cards'] = {
        "Lịch hôm nay": 0,
        "Chờ xác nhận": 0,
        "Tổng lịch hẹn": 0
    }
    lich_hen = None
    ho_so = None
    kw = request.args.get('kw')
    if active_tab == 'schedule':
        lich_hen = lich_hen_dao.get_lich_hen(page=int(request.args.get('page', 1)), kw=kw)
        print(lich.ho_ten for lich in lich_hen)
    if active_tab == 'profile':
        ho_so = ho_so_benh_nhan_dao.get_ho_so(page=int(request.args.get('page', 1)), kw=kw)
    return render_template('receptionist/receptionist.html',
                           active_tab=active_tab,
                           letan=True,
                           lich_hen=lich_hen,
                           ho_so=ho_so,
                           pages=math.ceil(lich_hen_dao.get_tong_lich_hen() / app.config['PAGE_SIZE']),
                           now=datetime.now().strftime("%Y-%m-%d"))


@app.route('/receptionist/add-appointment', methods=['POST'])
@receptionist_required
def add_appointment():
    try:
        ho_so_id = request.form.get('ho_so_id')
        bac_si_id = request.form.get('bac_si_id')
        ngay_dat = request.form.get('ngay_dat')
        gio_kham = request.form.get('gio_kham')
        dich_vu_id = request.form.get('dich_vu_id')
        ghi_chu = request.form.get('ghi_chu')
        lich_hen_dao.add_lich_hen(
            ho_so_benh_nhan_id=ho_so_id,
            ngay_dat=ngay_dat,
            gio_kham=gio_kham,
            bac_si_id=bac_si_id,
            dich_vu_id=dich_vu_id,
            ghi_chu=ghi_chu
        )
        flash("Tạo lịch thành công", 'success')
        print('success')
        return redirect('/receptionist')
    except Exception as ex:
        print('loi')
        flash("Tạo lịch thất bại", 'danger')
    return redirect('/receptionist')


@app.route('/receptionist/appointment/<int:lich_hen_id>', methods=['PUT'])
@receptionist_required
def accept_booked_appointment(lich_hen_id):
    try:
        lich_hen = lich_hen_dao.get_lich_hen_theo_id(lich_hen_id)
        lich_hen.trang_thai = TrangThaiLichHen.CHO_KHAM
        print(lich_hen)
        db.session.commit()
        return jsonify({'status': 'success', 'msg': 'Xác nhận thành công'})
    except Exception as ex:
        db.session.rollback()
        return jsonify({'status': 'error', 'msg': str(ex)})


@app.route('/receptionist/appointment/<int:lich_hen_id>', methods=['DELETE'])
@receptionist_required
def delete_booked_appointment(lich_hen_id):
    try:
        if lich_hen_dao.del_lich_hen(lich_hen_id):
            return jsonify({'status': 'success', 'msg': 'Xóa thành công'})
        else:
            return jsonify({'status': 'error', 'msg': 'Không có lịch hẹn cần xóa'})
    except Exception as ex:
        return jsonify({'status': 'error', 'msg': str(ex)})
