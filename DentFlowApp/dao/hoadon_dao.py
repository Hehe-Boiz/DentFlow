import datetime

from sqlalchemy import extract

from DentFlowApp.models import HoaDon


def get_ds_hoa_don_trong_thang(thang_nay=None, nam=None):
    now = datetime.datetime.now()
    if not thang_nay:
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


def get_doanh_thu_bac_si_trong_thang(thang_nay=None):
    ds_hoa_don = get_ds_hoa_don_trong_thang(thang_nay)
    thong_ke_doanh_thu_bac_si = {}
    for hoa_don in ds_hoa_don:
        ten_bac_si = hoa_don.phieu_dieu_tri.bac_si.ho_ten
        if ten_bac_si not in thong_ke_doanh_thu_bac_si:
            thong_ke_doanh_thu_bac_si[ten_bac_si] = {
                "tong_doanh_thu": 0,
                "so_luot_kham": 0,
                "trung_binh_kham": 0
            }
        thong_ke_doanh_thu_bac_si[ten_bac_si]['tong_doanh_thu'] += hoa_don.tong_tien
        thong_ke_doanh_thu_bac_si[ten_bac_si]['so_luot_kham'] += 1
    for ten_bac_si, so_lieu in thong_ke_doanh_thu_bac_si.items():
        if so_lieu['so_luot_kham'] > 0:
            so_lieu['trung_binh_kham'] = so_lieu['tong_doanh_thu'] / so_lieu['so_luot_kham']

    return thong_ke_doanh_thu_bac_si
