# from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Double
# from sqlalchemy.orm import relationship
#
# from DentFlowApp import db,app
# import enum
# from flask_login import UserMixin
# from sqlalchemy.sql import func
#
#
# class BaseModel(db.Model):
#     __abstract__ = True
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#
#
# class UserRole(enum.Enum):
#     ADMIN = 1
#     USER = 2
#     RECEPTIONIST = 3
#     DOCTOR = 4
#     CASHIER = 5
#
# class GioKham(enum.Enum):
#     Gio1 = '7:30'
#     Gio2 = '8:00'
#     Gio3 = '8:30'
#     Gio4 = '9:00'
#     Gio5 = '10:30'
#     Gio6 = '11:00'
#     Gio7 = '11:30'
#     Gio8 = '12:00'
#
# class CaLamViec(enum.Enum):
#     CaSang = 1
#     CaToi = 2
#
#
# class HoSoBenhNhan(db.Model):
#     maHoSo = Column(String(10), primary_key=True)
#     hoTen = Column(String(50), nullable=False)
#     soDienThoai = Column(Integer, nullable=False)
#     ngayTao = Column(DateTime(timezone=True), server_default=func.now())
#     ngaySua = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
#
#     def __str__(self):
#         return self.name
#
# class NguoiDung(BaseModel, UserMixin):
#     hoTen = Column(String(50), nullable=False)
#     avatar = Column(String(100))
#     username = Column(String(50), nullable=False, unique=True)
#     password = Column(String(50), nullable=False)
#     user_role = Column(Enum(UserRole), default=UserRole.USER)
#     soDienThoai = Column(Integer, nullable=False)
#     maHoSo = Column(String(10), ForeignKey(HoSoBenhNhan.maHoSo), nullable=True)
#
#     def __str__(self):
#         return self.name
#
# class ChuyenKhoa(db.Model):
#     maChuyenKhoa = Column(String(10), primary_key=True)
#     tenChuyenKhoa = Column(String(100), nullable=False)
#     cacBacSi = relationship('BacSi', backref='ChuyenKhoa', lazy=True)
#
#
# class BacSi(BaseModel):
#     maBacSi = Column(String(10), primary_key=True)
#     hoTen = Column(String(50), nullable=False)
#     soDienThoai = Column(Integer, nullable=False)
#     avatar = Column(String(100))
#     chuyenKhoa = Column(String(10), ForeignKey(ChuyenKhoa.maChuyenKhoa), nullable=False)
#     caLamViec = Column(Enum(CaLamViec), nullable=False)
#
#
# class DichVu(BaseModel):
#     tenDichVu = Column(String(100), nullable=False)
#     donGia = Column(Double, nullable=False)
#     chuyenKhoa = Column(String(10), ForeignKey(ChuyenKhoa.maChuyenKhoa), nullable=False)
#
# class LichHen(BaseModel):
#     ngayDat = Column(DateTime(timezone=True), server_default=func.now())
#     maHoSo = Column(String(10), ForeignKey(HoSoBenhNhan.maHoSo), nullable=False)
#     thoiGian = Column(Enum(GioKham), nullable=False)
#     dichVu = Column(Integer, ForeignKey(DichVu.id), nullable=False)
#     bacSi = Column(String(10), ForeignKey(BacSi.maBacSi), nullable=True)
#
#     def __str__(self):
#         return self.name
#
# class Thuoc(BaseModel):
#     pass
#
# class HoaDon(BaseModel):
#     pass
#
#
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         import hashlib
#         u = [
#              NguoiDung(name='receptionist', user_role=UserRole.RECEPTIONIST, phone='0123456',
#                   avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg',
#                   username='receptionist', password=str(hashlib.md5("123456".encode('utf-8')).hexdigest())),
#              NguoiDung(name='cashier', user_role=UserRole.CASHIER, phone='01234567',
#                   avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg',
#                   username='cashier', password=str(hashlib.md5("123456".encode('utf-8')).hexdigest())),
#              NguoiDung(name='user', user_role=UserRole.USER, phone='0123456',
#                   avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg',
#                   username='User', password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()))
#              ]
#         for user in u:
#             db.session.add(user)
#         db.session.commit()