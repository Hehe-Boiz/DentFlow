from DentFlowApp.models import LichLamViec, BacSi, TrangThaiLamViec, LichHen
from DentFlowApp import db
from datetime import date, datetime, timedelta
from sqlalchemy import and_
from DentFlowApp.utils import get_monday, get_sunday


def get_lich():
    return LichLamViec.query.all()


def get_lich_theo_bac_si_id(id):
    bac_si = BacSi.query.filter_by(ma_bac_si=id).first()
    if bac_si:
        danh_sach_lich = bac_si.lich_lam_viec_ds
        for lich in danh_sach_lich:
            print(f"Ngày: {lich.ngay}, Giờ: {lich.gio_bat_dau} - {lich.gio_ket_thuc}")
    return bac_si


def get_lich_san_sang_theo_ngay_theo_bac_si(ngay, bac_si_id):
    lich_kha_dung = LichLamViec.query.filter(LichLamViec.ngay_lam == ngay, LichLamViec.bac_si_id == bac_si_id
                                             , LichLamViec.trang_thai == TrangThaiLamViec.SAN_SANG).all()
    return lich_kha_dung


def get_lich_truc_hom_nay(bac_si_id):
    # Lấy lịch trực của bác sĩ đúng vào ngày hôm nay
    return LichLamViec.query.filter(
        LichLamViec.bac_si_id == bac_si_id,
        LichLamViec.ngay_lam == date.today()
    ).first()


def get_lich_lam_viec_by_bac_si_tuan_nay(bac_si_id):
    return LichLamViec.query.filter(
        LichLamViec.bac_si_id == bac_si_id,
        and_(
            LichLamViec.ngay_lam >= get_monday(date.today()),
            LichLamViec.ngay_lam <= get_sunday(date.today())
        )
    ).all()


def get_lich_lam_viec_theo_tuan(bac_si_id, date_chon):
    tu_ngay = get_monday(date_chon)
    den_ngay = get_sunday(date_chon)

    return LichLamViec.query.filter(
        LichLamViec.bac_si_id == bac_si_id,
        and_(
            LichLamViec.ngay_lam >= tu_ngay,
            LichLamViec.ngay_lam <= den_ngay
        )
    ).all()


