# FOR ROLE MANAGER
from DentFlowApp import app
from flask import render_template, jsonify, request

from DentFlowApp.dao.bacsi_dao import get_doctors
from DentFlowApp.dao.hoadon_dao import get_ds_hoa_don_trong_thang, get_soluong_hoa_don_trong_thang, \
    get_tong_doanh_thu_trong_thang, get_trung_binh_doanh_thu_trong_thang, get_doanh_thu_trong_ngay, \
    get_doanh_thu_bac_si_trong_thang, get_ds_hoa_don_trong_nam_ngay_gan_day, get_doanh_thu_trong_nam_ngay_gan_day
from DentFlowApp.dao.nhanvien_dao import get_ds_nhan_vien
from DentFlowApp.decorators import manager_required
import datetime

from DentFlowApp.models import PhieuDieuTri


def format_vnd(value):
    if not value:
        return "0 ₫"
    return "{:,.0f}".format(value).replace(",", ".") + " ₫"


@app.route('/manager', methods=['GET'])
@manager_required
def manager_view():
    ds_hoadon = get_ds_hoa_don_trong_thang()
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    active_tab = request.args.get('tab', 'thong-ke')
    ds_bacsi = get_doctors()
    cards = [
        {
            'title': 'Doanh thu hôm nay',
            'value': format_vnd(get_doanh_thu_trong_ngay()),  # Gọi hàm vừa viết
            'sub_text': datetime.datetime.now().strftime("Ngày %d/%m/%Y"),  # Hiện ngày tháng năm
            'class': 'bg-warning bg-gradient text-dark',  # Màu vàng cho nổi bật (hoặc bg-info text-white)
            'icon': 'fas fa-calendar-day'  # Icon lịch ngày
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
            'value': get_soluong_hoa_don_trong_thang(),
            'sub_text': 'Đã thanh toán trong tháng qua',
            'class': 'bg-primary bg-gradient text-white',

            'icon': 'fa-solid fa-receipt'
        },
        {
            'title': 'Trung bình hóa đơn',
            'value': format_vnd(get_trung_binh_doanh_thu_trong_thang()),
            'sub_text': 'Giá trị trung bình',
            'class': 'bg-success bg-gradient text-white',

            'icon': 'fas fa-tachometer-average'
        },
    ]

    return render_template('manager/trang_quanly.html', active_tab=active_tab, quanly=True, ds_hoadon=ds_hoadon,
                           cards=cards, now=now, ds_bacsi=ds_bacsi)


@app.route('/manager/statistics/monthly', methods=['GET'])
@manager_required
def manager_statistics_view():
    try:
        select_monthly = request.args.get('month', type=int)
        ds_hoadon = get_ds_hoa_don_trong_thang(thang_nay=select_monthly)

        data = list()
        for hoa_don in ds_hoadon:
            data.append({
                'ngay_thanh_toan': hoa_don.ngay_tao.strftime('%Y-%m-%d %H:%M:%S'),
                'tong_tien': hoa_don.tong_tien
            })
        return jsonify({
            'status': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403


@app.route('/manager/statistics/doctors', methods=['GET'])
@manager_required
def manager_statistics_doctors_view():
    try:
        thong_ke_bs = get_doanh_thu_bac_si_trong_thang()

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


@app.route('/manager/statistics/daily-recently', methods=['GET'])
@manager_required
def manager_statistics_daily_recently():
    try:
        so_lieu = get_doanh_thu_trong_nam_ngay_gan_day()
        data = list()
        for ngay_thanh_toan, doanh_thu in so_lieu.items():
            data.append({
                'ngay_thanh_toan': ngay_thanh_toan,
                'doanh_thu': doanh_thu,
            })
        return jsonify({'status': 'success', 'data': data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403

# @app.route
