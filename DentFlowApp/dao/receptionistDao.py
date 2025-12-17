from DentFlowApp.models import PhieuDieuTri, NguoiDung


def get_phieu_dieu_tri_by_maso(maso):
    return PhieuDieuTri.query.get(maso)


def get_users_by_something(something):
    return NguoiDung.query.get(something)


def get_profile_users_by_sdt_hoten(sdt=None, ho_ten=None, vai_tro=None, page=1):
    query = NguoiDung.query
    if sdt:
        query = query.filter(NguoiDung.so_dien_thoai.contains(sdt))
    if ho_ten:
        query = query.filter(NguoiDung.ho_ten.contains(ho_ten))
    if vai_tro:
        query = query.filter(NguoiDung.vai_tro == vai_tro)
    return query.paginate(page=page, per_page=5, error_out=False)


def create_profile(profile_user):
    patient_profile = NguoiDung()
    patient_profile.ho_ten = ho_ten
    patient_profile.so_dien_thoai = so_dien_thoai
    patient_profile.dia_chi = dia_chi
