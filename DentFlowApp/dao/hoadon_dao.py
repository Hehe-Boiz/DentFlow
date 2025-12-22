import datetime

from sqlalchemy import extract

from DentFlowApp.models import HoaDon


def get_all_hoa_don_trong_thang(thang_nay=None):
    now = datetime.datetime.now()
    if not thang_nay:
        thang_nay = now.month
    return HoaDon.query.filter(extract('month', HoaDon.ngay_thanh_toan) == thang_nay,
                               extract('year', HoaDon.ngay_thanh_toan) == now.year).all()


def get_soluong_hoa_don_trong_thang(thang_nay=None):
    return len(get_all_hoa_don_trong_thang(thang_nay))


def get_tong_doanh_thu_trong_thang(thang_nay=None):
    ds_hoadon = get_all_hoa_don_trong_thang(thang_nay)
    return sum(hoa_don.tong_tien for hoa_don in ds_hoadon)


def get_trung_binh_doanh_thu_trong_thang(thang_nay=None):
    so_luong = get_soluong_hoa_don_trong_thang(thang_nay)
    tong_doanh_thu = get_tong_doanh_thu_trong_thang(thang_nay)
    return tong_doanh_thu / so_luong


def get_doanh_thu_trong_ngay():
    now = datetime.datetime.now()
    ds_hoadon = HoaDon.query.filter(
        extract('day', HoaDon.ngay_thanh_toan) == now.day,
        extract('month', HoaDon.ngay_thanh_toan) == now.month,
        extract('year', HoaDon.ngay_thanh_toan) == now.year
    ).all()

    return sum(hoa_don.tong_tien for hoa_don in ds_hoadon)
