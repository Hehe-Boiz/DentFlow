from sqlalchemy.exc import IntegrityError

from DentFlowApp.models import LichHen
from DentFlowApp import db

def get_lich_hen():
    return LichHen.query.all()

def get_lich_hen_theo_id(id):
    return LichHen.query.get(id)

def get_lich_hen_theo_ngay_theo_bac_si(ngay, bac_si_id):
    return LichHen.query.filter(LichHen.bac_si_id == bac_si_id, LichHen.ngay_dat == ngay).all()

def add_lich_hen(ho_so_benh_nhan_id, bac_si_id, dich_vu_id,ngay_dat,gio_kham,ghi_chu):
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
