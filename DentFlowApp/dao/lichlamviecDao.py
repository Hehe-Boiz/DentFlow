from DentFlowApp.models import LichLamViec, BacSi
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
def get_schedules_by_day_by_doctor(day,id):
    lich_kha_dung = LichLamViec.query.filter(LichLamViec.ngay_lam == day, LichLamViec.bac_si_id == id).all()
    return lich_kha_dung