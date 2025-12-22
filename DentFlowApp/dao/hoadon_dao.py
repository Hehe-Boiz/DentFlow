from DentFlowApp.models import HoaDon


def get_all_hoa_don():
    return HoaDon.query.all()
