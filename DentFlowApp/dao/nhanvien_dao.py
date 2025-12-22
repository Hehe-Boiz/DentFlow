from DentFlowApp.models import NhanVien


def get_ds_nhan_vien():
    return NhanVien.query.all()
