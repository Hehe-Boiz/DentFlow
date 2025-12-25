from sqlalchemy.orm import joinedload

from DentFlowApp.models import DichVu, ChiTietPhieuDieuTri
from DentFlowApp import db,app


def get_dich_vu(page=-1, kw=None):
    query = DichVu.query
    if kw:
        query = query.filter(DichVu.ten_dich_vu.contains(kw))
    if page >= 1:
        start = (page - 1) * app.config['PAGE_SIZE']
        query = query.slice(start, start + app.config['PAGE_SIZE'])
    return query.all()


def get_services_by_id(id):
    return DichVu.query.get(id)


def add_dich_vu(phieu_dieu_tri_id,
                dich_vu_id,
                don_gia):
    dich_vu = ChiTietPhieuDieuTri(
        phieu_dieu_tri_id=phieu_dieu_tri_id,
        dich_vu_id=dich_vu_id,
        don_gia=don_gia
    )

    db.session.add(dich_vu)
    db.session.flush()
    return dich_vu
