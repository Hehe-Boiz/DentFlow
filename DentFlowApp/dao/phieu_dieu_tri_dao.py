from DentFlowApp.models import PhieuDieuTri
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
        patient_id=patient_id,
        chan_doan=chan_doan,
        ghi_chu=ghi_chu,
        bac_si_id=bac_si_id
    )
    db.session.add(phieu_dieu_tri)
    db.session.flush()

    return phieu_dieu_tri
