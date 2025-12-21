from DentFlowApp.models import PhieuDieuTri, TrangThaiThanhToan, DichVu


def get_phieu_dieu_tri_chua_thanh_toan(page=1):
    query = PhieuDieuTri.query
    query = query.filter(PhieuDieuTri.trang_thai_thanh_toan == TrangThaiThanhToan.CHUA_THANH_TOAN)
    query = query.order_by(PhieuDieuTri.ngay_tao.desc())
    return query.paginate(page=page, per_page=20, error_out=False)


def get_dich_vu_by_id(id_dich_vu):
    return DichVu.query.get(id_dich_vu)


def get_phieu_dieu_tri_da_thanh_toan_by_id(id):
    return PhieuDieuTri.query.filter(
        PhieuDieuTri.id == id and PhieuDieuTri.trang_thai_thanh_toan == TrangThaiThanhToan.DA_THANH_TOAN).first()


def get_ds_phieu_dieu_tri_da_thanh_toan(page=1):
    query = PhieuDieuTri.query
    query = query.filter(PhieuDieuTri.trang_thai_thanh_toan == TrangThaiThanhToan.DA_THANH_TOAN)
    query = query.order_by(PhieuDieuTri.ngay_tao)
    return query.paginate(page=page, per_page=20, error_out=False)
