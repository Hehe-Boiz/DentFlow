from DentFlowApp.models import LichLamViec, BacSi, TrangThaiLamViec
from DentFlowApp import db

def get_schedules():
    return LichLamViec.query.all()

def get_schedules_by_bac_si_id(id):
    bac_si = BacSi.query.filter_by(ma_bac_si=id).first()
    if bac_si:
        danh_sach_lich = bac_si.lich_lam_viec_ds
        for lich in danh_sach_lich:
            print(f"Ngày: {lich.ngay}, Giờ: {lich.gio_bat_dau} - {lich.gio_ket_thuc}")
    return bac_si
def get_schedules_is_ready_by_day_by_doctor(ngay , bac_si_id):
    lich_kha_dung = LichLamViec.query.filter(LichLamViec.ngay_lam == ngay, LichLamViec.bac_si_id == bac_si_id
                                             , LichLamViec.trang_thai == TrangThaiLamViec.SAN_SANG).all()
    return lich_kha_dung
