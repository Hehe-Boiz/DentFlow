from datetime import timedelta, datetime, time
from sqlalchemy import extract, func

from DentFlowApp import db
from DentFlowApp.models import HoaDon, PhieuDieuTri, BacSi, TrangThaiThanhToan


def get_thang_nam(thang_nay=None, nam_nay=None):
    now = datetime.now()
    if thang_nay == None:
        thang_nay = now.month
    if nam_nay == None:
        nam_nay = now.year
    return thang_nay, nam_nay


def get_ds_hoa_don_trong_thang(thang_nay=None, nam=None):
    thang_nay, nam_nay = get_thang_nam(thang_nay, nam)
    query = db.session.query(
        func.date(HoaDon.ngay_thanh_toan).label('ngay_thanh_toan'),
        func.sum(HoaDon.tong_tien).label('doanh_thu'),
    ).filter(
        extract('month', HoaDon.ngay_thanh_toan) == thang_nay,
        extract('year', HoaDon.ngay_thanh_toan) == nam_nay
    ).group_by(func.date(HoaDon.ngay_thanh_toan))
    return query.all()


def get_ds_doanh_thu_bac_si(bac_si_id: str = None):
    query = db.session.query(
        BacSi.ma_bac_si.label('ma_bac_si'),
        BacSi.ho_ten.label('ho_ten_bac_si'),
        func.sum(HoaDon.tong_tien).label('doanh_thu'),
        func.count(HoaDon.id).label('so_luot_kham'),
        func.avg(HoaDon.tong_tien).label('trung_binh_doanh_thu'),
    ).select_from(HoaDon)
    query = query.join(PhieuDieuTri).join(BacSi)
    if not bac_si_id:
        query = query.filter(PhieuDieuTri.trang_thai_thanh_toan == TrangThaiThanhToan.DA_THANH_TOAN).group_by(
            BacSi.ma_bac_si, BacSi.ho_ten)
        return query.all()
    else:
        query = query.filter(
            PhieuDieuTri.trang_thai_thanh_toan == TrangThaiThanhToan.DA_THANH_TOAN , BacSi.ma_bac_si == bac_si_id).group_by(
            BacSi.ma_bac_si, BacSi.ho_ten)
        return query.all()


def get_soluong_hoa_don_trong_thang(thang_nay=None, nam=None):
    thang_nay, nam_nay = get_thang_nam(thang_nay, nam)
    return HoaDon.query.filter(extract('month', HoaDon.ngay_thanh_toan) == thang_nay,
                               extract('year', HoaDon.ngay_thanh_toan) == nam_nay).count()


def get_doanh_thu_theo_bac_si(bac_si_id: str):
    query = db.session.query(
        BacSi.ho_ten.label('ho_ten_bac_si'),
        func.sum(HoaDon.tong_tien).label('doanh_thu'),
    )
    query = query.join(PhieuDieuTri).join(BacSi)
    query = query.filter(PhieuDieuTri.bac_si_id == bac_si_id).group_by(BacSi.ho_ten)
    return query.first()


def get_tong_doanh_thu_trong_thang(thang_nay=None, nam_nay=None):
    query = db.session.query(
        func.sum(HoaDon.tong_tien)
    )
    thang_nay, nam_nay = get_thang_nam(thang_nay, nam_nay)
    query = query.filter(extract('month', HoaDon.ngay_thanh_toan) == thang_nay)
    query = query.filter(extract('year', HoaDon.ngay_thanh_toan) == nam_nay)
    return query.scalar() or 0


def get_trung_binh_doanh_thu_trong_thang(thang_nay=None, nam_nay=None):
    query = db.session.query(
        func.avg(HoaDon.tong_tien)
    )
    thang_nay, nam_nay = get_thang_nam(thang_nay, nam_nay)
    query = query.filter(extract('month', HoaDon.ngay_thanh_toan) == thang_nay)
    query = query.filter(extract('year', HoaDon.ngay_thanh_toan) == nam_nay)
    return query.scalar() or 0


def get_doanh_thu_trong_ngay():
    now = datetime.now()
    tong_tien = db.session.query(func.sum(HoaDon.tong_tien)).filter(
        extract('day', HoaDon.ngay_thanh_toan) == now.day,
        extract('month', HoaDon.ngay_thanh_toan) == now.month,
        extract('year', HoaDon.ngay_thanh_toan) == now.year
    ).scalar()

    return tong_tien or 0


def get_doanh_thu_theo_so_ngay_gan_day(so_ngay):
    hom_nay = datetime.now()
    ngay_bat_dau = datetime.combine(hom_nay - timedelta(days=so_ngay - 1), time.min)

    query = db.session.query(
        func.date(HoaDon.ngay_thanh_toan).label('ngay'),
        func.sum(HoaDon.tong_tien).label('doanh_thu'),
    ).filter(
        HoaDon.ngay_thanh_toan >= ngay_bat_dau
    ).group_by(
        func.date(HoaDon.ngay_thanh_toan)
    ).order_by(
        func.date(HoaDon.ngay_thanh_toan)
    )
    return query.all()  # ngay_thanh_toan, doanh_thu


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


def get_so_lieu_bao_cao(thang_nay=None):
    ds_hoadon = get_ds_hoa_don_trong_thang(thang_nay)
    thong_ke = {}
    for hoa_don in ds_hoadon:
        if hoa_don.id not in thong_ke:
            thong_ke[hoa_don.id] = {
                'ngay_thanh_toan': hoa_don.ngay_thanh_toan,
                'tong_tien': 0,
            }
        thong_ke[hoa_don.id]['tong_tien'] += hoa_don.tong_tien

    return thong_ke
