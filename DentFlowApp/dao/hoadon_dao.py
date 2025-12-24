import datetime
from datetime import timedelta

from sqlalchemy import extract

from DentFlowApp.models import HoaDon


def get_ds_hoa_don_trong_thang(thang_nay=None, nam=None):
    now = datetime.datetime.now()
    if thang_nay == None:
        thang_nay = now.month
    if not nam:
        nam = now.year
    return HoaDon.query.filter(extract('month', HoaDon.ngay_thanh_toan) == thang_nay,
                               extract('year', HoaDon.ngay_thanh_toan) == nam).all()


def get_soluong_hoa_don_trong_thang(thang_nay=None):
    return len(get_ds_hoa_don_trong_thang(thang_nay))


def get_tong_doanh_thu_trong_thang(thang_nay=None):
    ds_hoadon = get_ds_hoa_don_trong_thang(thang_nay)
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


def get_ds_hoa_don_trong_nam_ngay_gan_day():
    now = datetime.datetime.now()
    bon_ngay_truoc = now - timedelta(days=4)
    ngay_bat_dau = bon_ngay_truoc.replace(hour=0, minute=0, second=0, microsecond=0)
    return HoaDon.query.filter(HoaDon.ngay_thanh_toan >= ngay_bat_dau).all()


def get_doanh_thu_trong_nam_ngay_gan_day():
    ds_hoadon = get_ds_hoa_don_trong_nam_ngay_gan_day()
    thong_ke = {}
    for hoa_don in ds_hoadon:
        ngay_thanh_toan = hoa_don.ngay_thanh_toan.strftime("%d/%m")
        if ngay_thanh_toan not in thong_ke:
            thong_ke[ngay_thanh_toan] = 0
        thong_ke[ngay_thanh_toan] += hoa_don.tong_tien
    return thong_ke


def get_doanh_thu_bac_si_trong_thang(thang_nay=None):
    ds_hoa_don = get_ds_hoa_don_trong_thang(thang_nay)
    thong_ke_doanh_thu_bac_si = {}
    for hoa_don in ds_hoa_don:
        ten_bac_si = hoa_don.phieu_dieu_tri.bac_si.ho_ten
        ma_bac_si = hoa_don.phieu_dieu_tri.bac_si.ma_bac_si
        ngay = hoa_don.ngay_thanh_toan.strftime('%Y-%m-%d %H:%M:%S')
        if ma_bac_si not in thong_ke_doanh_thu_bac_si:
            thong_ke_doanh_thu_bac_si[ma_bac_si] = {
                "tong_quat": {
                    "ten_bac_si": ten_bac_si,
                    "tong_doanh_thu": 0,
                    "so_luot_kham": 0,
                    "trung_binh_kham": 0
                },
                "chi_tiet": {}
            }

        thong_ke_doanh_thu_bac_si[ma_bac_si]["tong_quat"]['tong_doanh_thu'] += hoa_don.tong_tien
        thong_ke_doanh_thu_bac_si[ma_bac_si]["tong_quat"]['so_luot_kham'] += 1

        if ngay not in thong_ke_doanh_thu_bac_si[ma_bac_si]['chi_tiet']:
            thong_ke_doanh_thu_bac_si[ma_bac_si]['chi_tiet'][ngay] = 0
        thong_ke_doanh_thu_bac_si[ma_bac_si]['chi_tiet'][ngay] += hoa_don.tong_tien

    for ma_bac_si, so_lieu in thong_ke_doanh_thu_bac_si.items():
        if so_lieu['tong_quat']['so_luot_kham'] > 0:
            so_lieu['tong_quat']['trung_binh_kham'] = so_lieu['tong_quat']['tong_doanh_thu'] / so_lieu['tong_quat'][
                'so_luot_kham']

    return thong_ke_doanh_thu_bac_si


def get_chi_tiet_hoadon_trong_thang(thang_nay=None):
    ds_hoadon = get_ds_hoa_don_trong_thang(thang_nay)
    ct_hoadon = {}
    for hoa_don in ds_hoadon:
        ten_bac_si = hoa_don.phieu_dieu_tri.bac_si.ho_ten
        if ten_bac_si not in ct_hoadon:
            ct_hoadon[ten_bac_si] = {
                'ngay_thanh_toan': hoa_don.ngay_thanh_toan,
                'benh_nhan': hoa_don.phieu_dieu_tri.ho_so_benh_nhan.ho_ten,
                'dich_vu': [ct.ten_dich_vu for ct in hoa_don.phieu_dieu_tri.get_ds_dich_vu]

            }
