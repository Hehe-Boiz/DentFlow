from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, extract
from DentFlowApp.models import HoSoBenhNhan, LichHen, TrangThaiLichHen, DichVu, LichLamViec
from DentFlowApp import db, app
from flask_login import current_user
from DentFlowApp.dao import lichlamviec_dao
from sqlalchemy import func
from DentFlowApp.utils import get_monday, get_sunday
from datetime import date


def get_lich_hen(page=1, ho_so_benh_nhan_id=None, kw=None):
    query = LichHen.query
    query = query.options(
        joinedload(LichHen.ho_so_benh_nhan),
        joinedload(LichHen.bac_si)
    ).order_by(LichHen.ngay_dat.desc(), LichHen.gio_kham.desc())
    if kw:
        query = query.filter(HoSoBenhNhan.ho_ten.contains(kw))
    if ho_so_benh_nhan_id:
        query = query.filter(LichHen.ho_so_benh_nhan_id.__eq__(ho_so_benh_nhan_id))
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
        raise Exception('Rất tiêc, lịch hẹn của bạn vừa được người khác đặt cùng cách đây không lâu! Vui lòng đặt lại')


def del_lich_hen(lich_hen_id):
    lich_hen = get_lich_hen_theo_id(lich_hen_id)
    if not lich_hen:
        return False
    print(lich_hen)
    try:
        lich_hen.trang_thai = TrangThaiLichHen.HUY
        db.session.commit()
        return True
    except Exception as ex:
        db.session.rollback()
        raise Exception(str(ex))


def get_all_lich_hen_by_bac_si(bacsi_id):
    benh_nhan = (
        db.session.query(
            LichHen.id.label("lich_hen_id"),
            HoSoBenhNhan.id,
            HoSoBenhNhan.ho_ten,
            func.date_format(
                func.timestamp(LichHen.ngay_dat, LichHen.gio_kham),
                '%d/%m/%Y %H:%i'
            ).label("thoi_diem_kham_str"))
        .join(LichHen, LichHen.ho_so_benh_nhan_id == HoSoBenhNhan.id)
        .filter(
            LichHen.trang_thai == TrangThaiLichHen.CHO_KHAM
        ).distinct()
        .all()
    )

    return benh_nhan


def get_lich_hen_theo_bac_si_today_date_time(bacsi_id):
    # print(bacsi_id)
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
                '%d/%m/%Y %H:%i'
            ).label("thoi_diem_kham_str"))
        .join(LichHen, LichHen.ho_so_benh_nhan_id == HoSoBenhNhan.id)
        .filter(
            LichHen.bac_si_id == bacsi_id,
            LichHen.ngay_dat == lich_bac_si.ngay_lam,
            LichHen.gio_kham >= lich_bac_si.gio_bat_dau,
            LichHen.gio_kham <= lich_bac_si.gio_ket_thuc,
            LichHen.trang_thai == TrangThaiLichHen.CHO_KHAM,
        )
        .all()
    )

    return benh_nhan


def get_lich_hen_theo_bac_si_today_time(bacsi_id):
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
            or_(
                LichHen.trang_thai == TrangThaiLichHen.CHO_KHAM,
                LichHen.trang_thai == TrangThaiLichHen.DA_KHAM
            ),
            LichHen.ngay_dat == date.today()
        )
        .all()
    )

    return benh_nhan


def get_lich_hen_da_kham_theo_bac_si_today(bacsi_id):
    benh_nhan = (
        db.session.query(HoSoBenhNhan.id, HoSoBenhNhan.ho_ten)
        .join(LichHen, LichHen.ho_so_benh_nhan_id == HoSoBenhNhan.id)
        .filter(
            LichHen.bac_si_id == bacsi_id,
            LichHen.ngay_dat == date.today(),
            LichHen.trang_thai == TrangThaiLichHen.DA_KHAM,
        )
        .all()
    )

    return benh_nhan


def get_tong_lich_hen_theo_bac_si(bacsi_id):
    benh_nhan = (
        db.session.query(HoSoBenhNhan.id, HoSoBenhNhan.ho_ten)
        .join(LichHen, LichHen.ho_so_benh_nhan_id == HoSoBenhNhan.id)
        .filter(
            LichHen.bac_si_id == bacsi_id,
            # LichHen.gio_kham >= lich_bac_si.gio_bat_dau,
            LichHen.trang_thai == TrangThaiLichHen.DAT_LICH_THANH_CONG,
            LichHen.ngay_dat == date.today(),
        )
        .distinct()
        .all()
    )

    return benh_nhan


def get_tong_lich_hen_in_tuan_by_bac_si(bacsi_id):
    today = date.today()
    start_date = get_monday(today)
    end_date = get_sunday(today)
    benh_nhan = LichHen.query.filter(
        LichHen.bac_si_id == bacsi_id,
        LichHen.ngay_dat >= start_date,
        LichHen.ngay_dat <= end_date,

    )

    return benh_nhan


def get_lich_hen_by_bac_si_and_slot(bacsi_id, ngay_dat, gio_h):
    lich_hen = (LichHen.query
                .options(
        joinedload(LichHen.ho_so_benh_nhan),
        joinedload(LichHen.dich_vu)
    )
                .filter(
        LichHen.bac_si_id == bacsi_id,
        LichHen.ngay_dat == ngay_dat,
        extract('hour', LichHen.gio_kham) == gio_h,
    )
                .order_by(LichHen.gio_kham.asc())
                .all()
                )
    return lich_hen
