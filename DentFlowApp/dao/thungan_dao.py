from sqlalchemy.orm import joinedload

from DentFlowApp.models import PhieuDieuTri, TrangThaiThanhToan, DichVu


def get_phieu_dieu_tri_chua_thanh_toan(page=1, PAGE_SIZE=3):
    query = PhieuDieuTri.query
    query = query.filter(PhieuDieuTri.trang_thai_thanh_toan == TrangThaiThanhToan.CHUA_THANH_TOAN)
    query = query.options(
        joinedload(PhieuDieuTri.ho_so_benh_nhan),
        joinedload(PhieuDieuTri.bac_si),
        joinedload(PhieuDieuTri.chi_tiet_dich_vu)
    )
    query = query.order_by(PhieuDieuTri.ngay_tao.desc())
    return query.paginate(page=page, per_page=3, error_out=False)


def get_dich_vu_by_id(id_dich_vu):
    return DichVu.query.get(id_dich_vu)


def get_phieu_dieu_tri_da_thanh_toan_by_id(id):
    return PhieuDieuTri.query.filter(
        PhieuDieuTri.id == id and PhieuDieuTri.trang_thai_thanh_toan == TrangThaiThanhToan.DA_THANH_TOAN).first()


def get_ds_phieu_dieu_tri_da_thanh_toan(page=1, PAGE_SIZE=20):
    query = PhieuDieuTri.query
    query = query.filter(
        PhieuDieuTri.trang_thai_thanh_toan.in_([TrangThaiThanhToan.DA_THANH_TOAN, TrangThaiThanhToan.HOAN_TIEN]))
    query = query.options(
        joinedload(PhieuDieuTri.ho_so_benh_nhan),
        joinedload(PhieuDieuTri.bac_si),
        joinedload(PhieuDieuTri.chi_tiet_dich_vu)
    )
    query = query.order_by(PhieuDieuTri.ngay_tao)
    return query.paginate(page=page, per_page=PAGE_SIZE, error_out=False)


def get_tong_tien_by_phieu_dieu_tri(phieu_dieu_tri: PhieuDieuTri) -> float:
    tong_tien = 0
    for dich_vu in phieu_dieu_tri.chi_tiet_dich_vu:
        tong_tien += dich_vu.don_gia
    return tong_tien
