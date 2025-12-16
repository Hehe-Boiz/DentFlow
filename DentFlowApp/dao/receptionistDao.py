from DentFlowApp.models import PhieuDieuTri

def get_phieu_dieu_tri_by_maso(maso):
    return PhieuDieuTri.query.get(maso)

