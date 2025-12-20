from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from DentFlowApp.models import HoSoBenhNhan, LichHen, TrangThaiLichHen, DichVu
from DentFlowApp import db, app
from flask_login import current_user
from DentFlowApp.dao import lichlamviec_dao
from sqlalchemy import func


def get_lich_hen(page=1):
    query = LichHen.query
    query = query.options(
        joinedload(LichHen.ho_so_benh_nhan),
        joinedload(LichHen.bac_si)
    )
    if page:
        start = (page - 1) * app.config['PAGE_SIZE']
        query = query.slice(start, start + app.config['PAGE_SIZE'])
    return query.all()


def get_tong_lich_hen():
    return LichHen.query.count()


def get_lich_hen_theo_id(id):
    return LichHen.query.get(id)


def get_lich_hen_theo_ngay_theo_bac_si(ngay, bac_si_id):
    return LichHen.query.filter(LichHen.bac_si_id == bac_si_id, LichHen.ngay_dat == ngay).all()


def add_lich_hen(ho_so_benh_nhan_id, bac_si_id, dich_vu_id, ngay_dat, gio_kham, ghi_chu):
    lich_hen_moi = LichHen(
        ho_so_benh_nhan_id=ho_so_benh_nhan_id,
        bac_si_id=bac_si_id,
        dich_vu_id=dich_vu_id,
        ngay_dat=ngay_dat,
        gio_kham=gio_kham,
        ghi_chu=ghi_chu
    )
    db.session.add(lich_hen_moi)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Co loi xay ra')


def del_lich_hen(lich_hen_id):
    lich_hen = get_lich_hen_theo_id(lich_hen_id)
    if not lich_hen:
        return False
    print(lich_hen)
    try:
        db.session.delete(lich_hen)
        db.session.commit()
        return True
    except Exception as ex:
        db.session.rollback()
        raise Exception(str(ex))


def get_lich_hen_theo_bac_si_today_date_time(bacsi_id):
    # print(bacsi_id)
    lich_bac_si = lichlamviec_dao.get_lich_truc_hom_nay(bacsi_id)
    if not lich_bac_si:
        print(f"Bác sĩ {bacsi_id} không có lịch trực hôm nay.")
        return []
    # print(lich_bac_si.ngay_lam)
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


def get_lich_hen_theo_bac_si_today_time(bacsi_id):
    # print(bacsi_id)
    lich_bac_si = lichlamviec_dao.get_lich_truc_hom_nay(bacsi_id)
    if not lich_bac_si:
        print(f"Bác sĩ {bacsi_id} không có lịch trực hôm nay.")
        return []
    # print(lich_bac_si.ngay_lam)
    benh_nhan = (
        db.session.query(
            HoSoBenhNhan.id,
            HoSoBenhNhan.ho_ten,
            HoSoBenhNhan.so_dien_thoai,
            HoSoBenhNhan.gioi_tinh,
            func.date_format(HoSoBenhNhan.ngay_sinh, "%d/%m/%Y").label("ngay_sinh"),
            LichHen.gio_kham,
            LichHen.dich_vu_id,
            LichHen.ghi_chu,
            LichHen.trang_thai,
            DichVu.ten_dich_vu
        )
        .join(LichHen, LichHen.ho_so_benh_nhan_id == HoSoBenhNhan.id).join(DichVu, DichVu.id == LichHen.dich_vu_id)
        .filter(
            LichHen.bac_si_id == bacsi_id,
            LichHen.ngay_dat == lich_bac_si.ngay_lam,
            LichHen.gio_kham >= lich_bac_si.gio_bat_dau,
            LichHen.gio_kham <= lich_bac_si.gio_ket_thuc,
            or_(
                LichHen.trang_thai == TrangThaiLichHen.CHO_KHAM,
                LichHen.trang_thai == TrangThaiLichHen.DAT_LICH_THANH_CONG
            ),
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
