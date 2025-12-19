from DentFlowApp.models import Thuoc, LoThuoc
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
    """
    Tự động chọn lô thuốc phù hợp dựa trên số ngày dùng
    Ưu tiên: FEFO (First Expired First Out) - lô sắp hết hạn trước
    """
    ngay_hien_tai = date.today()
    try:
        ngay_ket_thuc_lieu_trinh = ngay_hien_tai + timedelta(days=int(so_ngay_dung))
    except ValueError:
        return None

    # Lấy lô thuốc còn hạn sau khi kết thúc liệu trình
    # Sắp xếp theo hạn sử dụng tăng dần (FEFO)
    lo_phu_hop = LoThuoc.query.filter(
        and_(
            LoThuoc.thuoc_id == thuoc_id,
            LoThuoc.han_su_dung >= ngay_ket_thuc_lieu_trinh, # Sửa > thành >= để chính xác hơn
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