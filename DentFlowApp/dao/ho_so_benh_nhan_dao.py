from DentFlowApp.models import HoSoBenhNhan
from DentFlowApp import app, db


def get_ho_so(page=1):
    query = HoSoBenhNhan.query
    if page:
        start = (page - 1) * app.config['PAGE_SIZE']
        query = query.slice(start, start + app.config['PAGE_SIZE'])
    return query.all()

def get_ho_so_theo_id(id):
    return HoSoBenhNhan.query.get(id)

def update_ho_so(ho_so_id,ho_ten,so_dien_thoai,dia_chi="",gioi_tinh=None,email="",ngay_sinh=None,CCCD=""):
    ho_so = get_ho_so_theo_id(ho_so_id)
    if not ho_so:
        return False
    ho_so.ho_ten = ho_ten
    ho_so.so_dien_thoai = so_dien_thoai
    ho_so.dia_chi = dia_chi
    ho_so.gioi_tinh = gioi_tinh
    ho_so.email = email
    ho_so.ngay_sinh = ngay_sinh
    ho_so.CCCD = CCCD
    print(ho_so.CCCD, ho_so.gioi_tinh, ho_so.ngay_sinh, ho_so.CCCD, ho_so.email, ho_so.ho_ten)
    try:
        db.session.commit()
        return True
    except Exception as ex:
        db.session.rollback()
        raise Exception(str(ex))