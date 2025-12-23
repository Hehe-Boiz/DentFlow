from DentFlowApp.models import PhieuDieuTri, LieuLuongSuDung, DonThuoc
from DentFlowApp import db
from datetime import date
from sqlalchemy.exc import IntegrityError


def add_phieu_dieu_tri(patient_id, chan_doan, ghi_chu, bac_si_id):
    phieu_dieu_tri = PhieuDieuTri(
        patient_id=patient_id,
        chan_doan=chan_doan,
        ghi_chu=ghi_chu,
        bac_si_id=bac_si_id
    )
    db.session.add(phieu_dieu_tri)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Co loi xay ra')


def add_phieu_dieu_tri_flush(patient_id, chan_doan, ghi_chu, bac_si_id):
    phieu_dieu_tri = PhieuDieuTri(
        ho_so_benh_nhan_id=patient_id,
        chan_doan=chan_doan,
        ghi_chu=ghi_chu,
        bac_si_id=bac_si_id
    )
    db.session.add(phieu_dieu_tri)
    db.session.flush()

    return phieu_dieu_tri


def get_phieu_dieu_tri_by_ma_bacsi(ma_bacsi):
    query = PhieuDieuTri.query.filter_by(PhieuDieuTri.ma_bacsi == ma_bacsi).all()


def get_ds_thuoc_by_phieu_dieu_tri(id):
    query = DonThuoc.query.filter(DonThuoc.phieu_dieu_tri_id == id).first()
    query_lieuluong = LieuLuongSuDung.query.filter(LieuLuongSuDung.don_luog_id == query.id).first()
    return query_lieuluong  # so_luong && query_lieuluong.thuoc.don_gia && query_lieuluong.thuoc.ten_thuoc
