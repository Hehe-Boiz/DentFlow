from DentFlowApp.models import DichVu
from DentFlowApp import db


def get_services():
    return DichVu.query.all()


def get_services_by_id(id):
    return DichVu.query.get(id)


def add_dich_vu(phieu_dieu_tri_id,
                dich_vu_id,
                don_gia):
    dich_vu = DichVu(
        phieu_dieu_tri_id=phieu_dieu_tri_id,
        dich_vu_id=dich_vu_id,
        don_gia=don_gia
    )

    db.session.add(dich_vu)
    db.session.flush()
    return dich_vu
