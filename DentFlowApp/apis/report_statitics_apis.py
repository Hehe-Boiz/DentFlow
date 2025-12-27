from DentFlowApp import app
from flask import render_template, jsonify, request

from DentFlowApp.dao.bacsi_dao import get_doctors
from DentFlowApp.dao.hoadon_dao import get_ds_hoa_don_trong_thang, get_soluong_hoa_don_trong_thang, \
    get_tong_doanh_thu_trong_thang, get_trung_binh_doanh_thu_trong_thang, get_doanh_thu_trong_ngay, \
    get_doanh_thu_bac_si_trong_thang, \
    get_doanh_thu_theo_so_ngay_gan_day, get_ds_doanh_thu_bac_si
from DentFlowApp.dao.nhanvien_dao import get_ds_nhan_vien
from DentFlowApp.decorators import manager_required
import datetime


def format_vnd(value):
    if not value:
        return "0 ₫"
    return "{:,.0f}".format(value).replace(",", ".") + " ₫"


@app.route('/manager', methods=['GET'])
@manager_required
def manager_view():
    ds_hoadon = get_ds_hoa_don_trong_thang()
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    month = int(datetime.datetime.now().strftime('%m'))
    active_tab = request.args.get('tab', 'thong-ke')
    ds_bacsi = get_doctors()
    page = request.args.get('page', 1, type=int)
    cards = [
        {
            'title': 'Doanh thu hôm nay',
            'value': format_vnd(get_doanh_thu_trong_ngay()),
            'sub_text': datetime.datetime.now().strftime("Ngày %d/%m/%Y"),
            'class': 'bg-warning bg-gradient text-dark',
            'icon': 'fas fa-calendar-day'
        },
        {
            'title': 'Tổng doanh thu',
            'value': format_vnd(get_tong_doanh_thu_trong_thang()),
            'sub_text': 'Trong tháng qua',
            'class': 'bg-danger bg-gradient text-white',
            'icon': 'fas fa-chart-bar'
        },
        {
            'title': 'Tổng hóa đơn',
            'value': get_soluong_hoa_don_trong_thang(thang_nay=month),
            'sub_text': 'Đã thanh toán trong tháng qua',
            'class': 'bg-primary bg-gradient text-white',

            'icon': 'fa-solid fa-receipt'
        },
        {
            'title': 'Trung bình hóa đơn',
            'value': format_vnd(get_trung_binh_doanh_thu_trong_thang(thang_nay=month)),
            'sub_text': 'Giá trị trung bình',
            'class': 'bg-success bg-gradient text-white',

            'icon': 'fas fa-tachometer-average'
        },
    ]

    return render_template('manager/trang_quanly.html', active_tab=active_tab, quanly=True, ds_hoadon=ds_hoadon,
                           cards=cards, now=now, ds_bacsi=ds_bacsi, page=page)


@app.route('/manager/statistics/daily-recently', methods=['GET'])
@manager_required
def manager_statistics_daily_recently():
    try:
        so_lieu = get_doanh_thu_theo_so_ngay_gan_day(so_ngay=5)
        data = [{
            'ngay_thanh_toan': str(r.ngay),
            'doanh_thu': r.doanh_thu or 0,
        } for r in so_lieu]
        return jsonify({'status': 'success', 'data': data}), 200
    except Exception as e:
        return jsonify(
            {'status': 'error', 'message': f'Đã có lỗi xảy ra khi lấy thống kê doanh thu {str(e)}: {e}'}), 500


@app.route('/manage/statistics/monthly-only', methods=['GET'])
@manager_required
def manager_monthly_only():
    try:
        select_monthly = request.args.get('month')
        select_monthly = select_monthly if select_monthly else datetime.datetime.now().month
        so_lieu = get_ds_hoa_don_trong_thang(thang_nay=select_monthly)
        data = [
            {
                'ngay_thanh_toan': str(r.ngay_thanh_toan),
                'doanh_thu': r.doanh_thu or 0
            } for r in so_lieu
        ]
        return jsonify(
            {'status': 'success', 'data': data,
             'month': select_monthly})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/manage/statistics/doctors-only', methods=['GET'])
@manager_required
def manager_doctors_only():
    try:
        selected_doctor = request.args.get('doctor', type=str)
        so_lieu = get_ds_doanh_thu_bac_si(selected_doctor)
        data = [
            {
                'ho_ten_bac_si': str(r.ho_ten_bac_si),
                'doanh_thu': r.doanh_thu or 0,
                'so_luot_kham': r.so_luot_kham,
                'trung_binh_doanh_thu': r.trung_binh_doanh_thu
            } for r in so_lieu
        ]
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/manager/statistics/monthly', methods=['GET'])
@manager_required
def manager_statistics_view():
    try:
        select_monthly = request.args.get('month', type=int)
        so_lieu = get_ds_hoa_don_trong_thang(thang_nay=select_monthly)

        return jsonify({
            'status': 'success',
            # 'data': data,
            # 'data_ds_hoadon': data_ds_hoadon
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/manager/statistics/doctors', methods=['GET'])
@manager_required
def manager_statistics_doctors_view():
    try:
        select_monthly = request.args.get('month', type=int)
        thong_ke_bs = get_doanh_thu_bac_si_trong_thang(select_monthly)

        data = list()
        data_daily = {}

        for ma_bac_si, so_lieu in thong_ke_bs.items():
            tong_quat = so_lieu['tong_quat']
            chi_tiet = so_lieu['chi_tiet']
            data.append({
                'ten_bac_si': tong_quat['ten_bac_si'],
                'ma_bac_si': ma_bac_si,
                'tong_doanh_thu': tong_quat['tong_doanh_thu'],
                'so_luot_kham': tong_quat['so_luot_kham'],
                'trung_binh_kham': tong_quat['trung_binh_kham'],
            })
            chi_tiet_list = list()
            for ngay_thanh_toan, tong_tien in chi_tiet.items():
                chi_tiet_list.append({
                    'ngay_thanh_toan': ngay_thanh_toan,
                    'tong_tien': tong_tien
                })

            data_daily[ma_bac_si] = chi_tiet_list
        return jsonify({
            'status': 'success',
            'data': data,
            'data_daily': data_daily
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403


@app.route('/manager/nhan-vien', methods=['GET'])
@manager_required
def manage_nhanvien_view():
    try:
        ds_nhanvien = get_ds_nhan_vien()
        data = list()
        for nhan_vien in ds_nhanvien:
            data.append({
                'ma_nhan_vien': nhan_vien.ma_nv,
                'ho_ten': nhan_vien.ho_ten,
                'nam_sinh': nhan_vien.nam_sinh,
                'so_dien_thoai': nhan_vien.so_dien_thoai,
                'ngay_vao_lam': nhan_vien.ngay_vao_lam,
            })
        return jsonify({'status': 'success', 'data': data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403
