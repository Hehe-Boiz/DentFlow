# FOR ROLE MANAGER

from DentFlowApp import app
from flask import render_template, jsonify

from DentFlowApp.dao.hoadon_dao import get_all_hoa_don_trong_thang, get_soluong_hoa_don_trong_thang, \
    get_tong_doanh_thu_trong_thang, get_trung_binh_doanh_thu_trong_thang, get_doanh_thu_trong_ngay
from DentFlowApp.decorators import manager_required
import datetime


def format_vnd(value):
    if not value:
        return "0 ₫"
    return "{:,.0f}".format(value).replace(",", ".") + " ₫"


@app.route('/manager', methods=['GET'])
@manager_required
def manager_view():
    ds_hoadon = get_all_hoa_don_trong_thang()

    cards = [
        {
            'title': 'Doanh thu hôm nay',
            'value': format_vnd(get_doanh_thu_trong_ngay()),  # Gọi hàm vừa viết
            'sub_text': datetime.datetime.now().strftime("Ngày %d/%m/%Y"),  # Hiện ngày tháng năm
            'class': 'bg-warning text-dark',  # Màu vàng cho nổi bật (hoặc bg-info text-white)
            'icon': 'fas fa-calendar-day'  # Icon lịch ngày
        },
        {
            'title': 'Tổng doanh thu',
            'value': format_vnd(get_tong_doanh_thu_trong_thang()),
            'sub_text': 'Trong tháng qua',
            'class': 'bg-danger text-white',
            'icon': 'fas fa-chart-bar'
        },
        {
            'title': 'Tổng hóa đơn',
            'value': get_soluong_hoa_don_trong_thang(),
            'sub_text': 'Đã thanh toán trong tháng qua',
            'class': 'bg-primary text-white',

            'icon': 'fa-solid fa-receipt'
        },
        {
            'title': 'Trung bình hóa đơn',
            'value': format_vnd(get_trung_binh_doanh_thu_trong_thang()),
            'sub_text': 'Giá trị trung bình',
            'class': 'bg-success text-white',

            'icon': 'fas fa-tachometer-average'
        },
    ]
    return render_template('manager/manager.html', quanly=True, ds_hoadon=ds_hoadon, cards=cards)


@app.route('/manager/statistics', methods=['GET'])
@manager_required
def manager_statistics_view():
    try:
        ds_hoadon = get_all_hoa_don_trong_thang()
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
