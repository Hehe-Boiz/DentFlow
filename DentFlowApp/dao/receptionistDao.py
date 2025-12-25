from DentFlowApp.models import PhieuDieuTri, NguoiDung, HoSoBenhNhan


def get_phieu_dieu_tri_by_id(id):
    return PhieuDieuTri.query.get(id)


def get_nguoi_dung_by_sdt_hoten(sdt=None, ho_ten=None, vai_tro=None, page=1):
    query = NguoiDung.query
    if sdt:
        query = query.filter(NguoiDung.so_dien_thoai.contains(sdt))
    if ho_ten:
        query = query.filter(NguoiDung.ho_ten.contains(ho_ten))
    if vai_tro:
        query = query.filter(NguoiDung.vai_tro == vai_tro)
    return query.paginate(page=page, per_page=5, error_out=False)


def get_ho_so_benh_nhan_by_hoten_sodienthoai(ho_ten, so_dien_thoai):
    if not ho_ten or not so_dien_thoai:
        return None
    return HoSoBenhNhan.query.filter(
        HoSoBenhNhan.ho_ten == ho_ten.strip(),
        HoSoBenhNhan.so_dien_thoai == so_dien_thoai.strip()
    ).first()
