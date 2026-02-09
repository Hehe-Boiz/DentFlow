import datetime
from datetime import timedelta, datetime as dt
from sqlalchemy import extract, func
from DentFlowApp import db  
from DentFlowApp.models import HoaDon, PhieuDieuTri, BacSi

def get_ds_hoa_don_trong_thang(thang_nay=None, nam=None):
    now = datetime.datetime.now()
    thang_nay = thang_nay or now.month
    nam = nam or now.year
    return HoaDon.query.filter(
        extract('month', HoaDon.ngay_thanh_toan) == thang_nay,
        extract('year', HoaDon.ngay_thanh_toan) == nam
    )

def get_soluong_hoa_don_trong_thang(thang_nay=None):
    return get_ds_hoa_don_trong_thang(thang_nay).count()

def get_tong_doanh_thu_trong_thang(thang_nay=None):
    total = db.session.query(func.coalesce(func.sum(HoaDon.tong_tien), 0)).filter(
        extract('month', HoaDon.ngay_thanh_toan) == (thang_nay or dt.now().month),
        extract('year', HoaDon.ngay_thanh_toan) == dt.now().year
    ).scalar()
    return total

def get_trung_binh_doanh_thu_trong_thang(thang_nay=None):
    avg = db.session.query(func.avg(HoaDon.tong_tien)).filter(
        extract('month', HoaDon.ngay_thanh_toan) == (thang_nay or dt.now().month),
        extract('year', HoaDon.ngay_thanh_toan) == dt.now().year
    ).scalar()
    return avg or 0

def get_doanh_thu_trong_ngay():
    today = dt.now().date()
    total = db.session.query(func.coalesce(func.sum(HoaDon.tong_tien), 0)).filter(
        func.date(HoaDon.ngay_thanh_toan) == today
    ).scalar()
    return total

def get_ds_hoa_don_trong_nam_ngay_gan_day():
    four_days_ago = dt.now() - timedelta(days=4)
    return HoaDon.query.filter(
        HoaDon.ngay_thanh_toan >= four_days_ago
    )

def get_doanh_thu_trong_nam_ngay_gan_day():
    grouped_data = db.session.query(
        func.strftime("%d/%m", HoaDon.ngay_thanh_toan).label('date'),
        func.sum(HoaDon.tong_tien).label('total')
    ).filter(
        HoaDon.ngay_thanh_toan >= (dt.now() - timedelta(days=4))
    ).group_by('date').all()
    return {date: total for date, total in grouped_data}

def get_doanh_thu_bac_si_trong_thang(thang_nay=None):
    from sqlalchemy.orm import aliased
    
    BacSiAlias = aliased(BacSi)
    current_month = dt.now().month
    current_year = dt.now().year
    
    tong_quat = db.session.query(
        BacSiAlias.ma_bac_si,
        BacSiAlias.ho_ten,
        func.sum(HoaDon.tong_tien).label('tong_doanh_thu'),
        func.count(HoaDon.id).label('so_luot_kham')
    ).join(
        PhieuDieuTri, PhieuDieuTri.bac_si_id == BacSiAlias.id
    ).join(
        HoaDon, HoaDon.phieu_dieu_tri_id == PhieuDieuTri.id
    ).filter(
        extract('month', HoaDon.ngay_thanh_toan) == current_month,
        extract('year', HoaDon.ngay_thanh_toan) == current_year
    ).group_by(BacSiAlias.ma_bac_si).subquery()
    
    chi_tiet = db.session.query(
        BacSi.ma_bac_si,
        func.strftime('%Y-%m-%d %H:%M:%S', HoaDon.ngay_thanh_toan).label('ngay'),
        func.sum(HoaDon.tong_tien).label('tien_ngay')
    ).join(
        PhieuDieuTri, PhieuDieuTri.bac_si_id == BacSi.id
    ).join(
        HoaDon, HoaDon.phieu_dieu_tri_id == PhieuDieuTri.id
    ).filter(
        extract('month', HoaDon.ngay_thanh_toan) == current_month,
        extract('year', HoaDon.ngay_thanh_toan) == current_year
    ).group_by(
        BacSi.ma_bac_si, 'ngay'
    ).subquery()
    
    # Combine all data
    result = {}
    tong_quat_data = db.session.query(
        tong_quat.c.ma_bac_si,
        tong_quat.c.ho_ten,
        tong_quat.c.tong_doanh_thu,
        tong_quat.c.so_luot_kham
        )
    for ma_bs, ten_bs, tong_tien, so_luot in tong_quat_data:
        trung_binh = tong_tien / so_luot if so_luot > 0 else 0
        result[ma_bs] = {
            "tong_quat": {
                "ten_bac_si": ten_bs,
                "tong_doanh_thu": tong_tien,
                "so_luot_kham": so_luot,
                "trung_binh_kham": trung_binh
            },
            "chi_tiet": {}
        }
    
    chi_tiet_data = db.session.query(
        chi_tiet.c.ma_bac_si,
        chi_tiet.c.ngay,
        chi_tiet.c.tien_ngay
        )
    for ma_bs, ngay, tien in chi_tiet_data:
        if ma_bs in result:
            result[ma_bs]["chi_tiet"][ngay] = tien
    
    return result

def get_so_lieu_bao_cao(thang_nay=None):
    ds_hoadon = get_ds_hoa_don_trong_thang(thang_nay).all()
    return {
        hd.id: {
            'ngay_thanh_toan': hd.ngay_thanh_toan,
            'tong_tien': hd.tong_tien  
        } for hd in ds_hoadon
    }
