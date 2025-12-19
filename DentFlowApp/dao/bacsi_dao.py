from DentFlowApp.models import BacSi, UserRole, TrangThaiLamViec, LichLamViec
from DentFlowApp import db

def get_doctors():
    return BacSi.query.all()

def get_doctors_is_ready():
    return BacSi.query.join(LichLamViec).filter(LichLamViec.trang_thai==TrangThaiLamViec.SAN_SANG).all()

def get_doctors_by_id(id):
    return BacSi.query.get(id)

def get_doctors_by_user_id(nguoi_dung_id):
    return BacSi.query.filter_by(nguoi_dung_id=nguoi_dung_id).first()