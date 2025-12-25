from DentFlowApp.models import Thuoc, LoThuoc, DonThuoc, LieuLuongSuDung
from DentFlowApp import db
from datetime import date, timedelta
from sqlalchemy import and_


def get_thuoc_all():
    """Lấy tất cả thuốc"""
    return Thuoc.query.all()


def get_thuoc_by_id(thuoc_id):
    """Lấy thông tin thuốc theo ID"""
    return Thuoc.query.get(thuoc_id)


def get_lo_thuoc_by_thuoc_id(thuoc_id):
    """Lấy tất cả lô thuốc còn hạn và còn tồn kho"""
    ngay_hien_tai = date.today()
    return LoThuoc.query.filter(
        and_(
            LoThuoc.thuoc_id == thuoc_id,
            LoThuoc.han_su_dung > ngay_hien_tai,
            LoThuoc.so_luong > 0
        )
    ).order_by(LoThuoc.han_su_dung.asc()).all()


def get_lo_thuoc_phu_hop(thuoc_id, so_ngay_dung):
    ngay_hien_tai = date.today()
    try:
        ngay_ket_thuc_lieu_trinh = ngay_hien_tai + timedelta(days=int(so_ngay_dung))
    except ValueError:
        return None

    lo_phu_hop = LoThuoc.query.filter(
        and_(
            LoThuoc.thuoc_id == thuoc_id,
            LoThuoc.han_su_dung >= ngay_ket_thuc_lieu_trinh,
            LoThuoc.so_luong > 0
        )
    ).order_by(LoThuoc.han_su_dung.asc()).first()

    return lo_phu_hop


def get_lo_co_han_xa_nhat(thuoc_id):
    """
    Tìm lô thuốc có hạn sử dụng xa nhất còn trong kho (để tính max days)
    """
    ngay_hien_tai = date.today()
    return LoThuoc.query.filter(
        and_(
            LoThuoc.thuoc_id == thuoc_id,
            LoThuoc.han_su_dung > ngay_hien_tai,
            LoThuoc.so_luong > 0
        )
    ).order_by(LoThuoc.han_su_dung.desc()).first()


def add_don_thuoc_add_flush(phieu_dieu_tri_id):
    phieu_dieu_tri = DonThuoc(
        phieu_dieu_tri_id=phieu_dieu_tri_id,
    )
    db.session.add(phieu_dieu_tri)
    db.session.flush()
    return phieu_dieu_tri


def add_lieu_thuoc_add_flush(don_thuoc_id, thuoc_id, so_luong, huong_dan):
    lieu_thuoc = LieuLuongSuDung(
        don_thuoc_id=don_thuoc_id,
        thuoc_id=thuoc_id,
        so_luong=so_luong,
        huong_dan=huong_dan,
    )

    db.session.add(lieu_thuoc)
    db.session.flush()
    return lieu_thuoc
