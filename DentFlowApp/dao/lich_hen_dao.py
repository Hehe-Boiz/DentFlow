from DentFlowApp.models import HoSoBenhNhan, LichHen, TrangThaiLichHen
from DentFlowApp import db
from flask_login import current_user
from DentFlowApp.dao import lichlamviec_dao
from sqlalchemy import func


def get_lich_hen_theo_bac_si():
    bacsi_id = current_user.bac_si.ma_bac_si
    print(bacsi_id)
    lich_bac_si = lichlamviec_dao.get_lich_truc_hom_nay(bacsi_id)
    if not lich_bac_si:
        print(f"Bác sĩ {bacsi_id} không có lịch trực hôm nay.")
        return []
    print(lich_bac_si.ngay_lam)
    benh_nhan = (
        db.session.query(
            HoSoBenhNhan.id,
            HoSoBenhNhan.ho_ten,
            func.date_format(
                func.timestamp(LichHen.ngay_dat, LichHen.gio_kham),
                '%d/%m/%Y %H:%i'  # MySQL dùng %i cho phút
            ).label("thoi_diem_kham_str"))
        .join(LichHen, LichHen.ho_so_benh_nhan_id == HoSoBenhNhan.id)
        .filter(
            LichHen.bac_si_id == bacsi_id,
            LichHen.ngay_dat == lich_bac_si.ngay_lam,
            LichHen.gio_kham >= lich_bac_si.gio_bat_dau,
            LichHen.gio_kham <= lich_bac_si.gio_ket_thuc,
            LichHen.trang_thai == TrangThaiLichHen.CHO_KHAM,
        )
        .distinct()  # phòng trường hợp 1 bệnh nhân có nhiều lịch trong khung giờ
        .all()
    )

    return benh_nhan

def get_lich_hen_da_kham_theo_bac_si():
    bacsi_id = current_user.bac_si.ma_bac_si
    lich_bac_si = lichlamviec_dao.get_lich_by_bac_si_id(bacsi_id)
    benh_nhan = (
        db.session.query(HoSoBenhNhan.id, HoSoBenhNhan.ho_ten)
        .join(LichHen, LichHen.ho_so_benh_nhan_id == HoSoBenhNhan.id)
        .filter(
            LichHen.bac_si_id == bacsi_id,
            LichHen.gio_kham >= lich_bac_si.gio_bat_dau,
            LichHen.gio_kham <= lich_bac_si.gio_ket_thuc,
            LichHen.trang_thai == TrangThaiLichHen.DA_KHAM,
        )
        .distinct()  # phòng trường hợp 1 bệnh nhân có nhiều lịch trong khung giờ
        .all()
    )

    return benh_nhan

def get_tong_lich_hen_theo_bac_si():
    bacsi_id = current_user.bac_si.ma_bac_si
    lich_bac_si = lichlamviec_dao.get_lich_by_bac_si_id(bacsi_id)
    benh_nhan = (
        db.session.query(HoSoBenhNhan.id, HoSoBenhNhan.ho_ten)
        .join(LichHen, LichHen.ho_so_benh_nhan_id == HoSoBenhNhan.id)
        .filter(
            LichHen.bac_si_id == bacsi_id,
            LichHen.gio_kham >= lich_bac_si.gio_bat_dau,
            LichHen.trang_thai == TrangThaiLichHen.DAT_LICH_THANH_CONG,
        )
        .distinct()  # phòng trường hợp 1 bệnh nhân có nhiều lịch trong khung giờ
        .all()
    )

    return benh_nhan

