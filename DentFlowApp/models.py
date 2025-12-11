from sqlalchemy import Column, Integer, String, Enum as sqlEnum, DateTime, Date, Time, Double, ForeignKey
from sqlalchemy.orm import relationship

from DentFlowApp import db, app
from enum import Enum as UserEnum
from flask_login import UserMixin
from datetime import datetime
from enum import Enum


class GioiTinh(Enum):
    NAM = 'Nam'
    NU = 'Nu'
    KHAC = 'Khac'


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(UserEnum):
    ADMIN = 1
    USER = 2
    RECEPTIONIST = 3
    DOCTOR = 4
    CASHIER = 5


class User(BaseModel, UserMixin):
    name = Column(String(50), nullable=False)
    avatar = Column(String(100))
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    user_role = Column(sqlEnum(UserRole), default=UserRole.USER)
    phone = Column(Integer, nullable=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Ma USER: {self.id}>"


class HoSoBenhNhan(db.Model):
    __tablename__ = "ho_so_benh_nhan"
    ma_ho_so = Column(String(20), primary_key=True)
    ho_ten = Column(String(50), nullable=False)
    so_dien_thoai = Column(Integer, nullable=False)
    ngay_tao = Column(DateTime, default=datetime.utcnow, nullable=False)
    dia_chi = Column(String(255), nullable=True)
    gioi_tinh = Column(sqlEnum(GioiTinh), nullable=False)

    lich_hen = relationship(
        "LichHen",
        back_populates="ho_so_benh_nhan",
        cascade="all, delete-orphan"
    )
    phieu_dieu_tri = relationship(
        "PhieuDieuTri",
        back_populates="ho_so_benh_nhan",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<HoSoBenhNhan  {self.ma_ho_so}>"


class LichHen(BaseModel):
    # ma_lich_hen = super().id
    ngay_dat = Column(DateTime, default=datetime.utcnow)

    ho_so_benh_nhan_id = Column(String(20), ForeignKey(HoSoBenhNhan.ma_ho_so), nullable=False)
    bac_si_id = Column(Integer, ForeignKey("bac_si.ma_bac_si"), nullable=True)
    thoi_gian_id = Column(Integer, ForeignKey("thoi_gian.id"), nullable=True)
    dich_vu_id = Column(String(20), ForeignKey("dich_vu.ma_dv"), nullable=True)

    ho_so_benh_nhan = relationship("HoSoBenhNhan", back_populates="lich_hen")
    bac_si = relationship("BacSi", back_populates="lich_hen")
    thoi_gian = relationship("ThoiGian", back_populates="lich_hen")
    dich_vu = relationship("DichVu", back_populates="lich_hen")

    def __repr__(self):
        return f"<MaLichHen: {self.id}>"


class BacSi(db.Model):
    ma_bac_si = Column(Integer, ForeignKey("user.id"), primary_key=True)
    phieu_dieu_tri = relationship(
        "PhieuDieuTri",
        back_populates="bac_si",
        cascade="all, delete-orphan"
    )
    # 0..5
    lich_hen = relationship(
        "LichHen",
        back_populates="bac_si",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<MaBacSi: {self.ma_bac_si}>"


class BacSiLichHanhChinh(BacSi):
    thu = Column(Integer, nullable=False)


class BacSiLichDangKy(BacSi):
    ngay = Column(Date, nullable=False)
    gio_bat_dau = Column(Time, nullable=False)
    gio_ket_thuc = Column(Time, nullable=False)


class ThoiGian(BaseModel):
    thoi_gian = Column(Time, nullable=False)
    lich_hen = relationship(
        "LichHen",
        back_populates="thoi_gian"
    )
    def __repr__(self):
        return f"<MaTime: {self.id}>"


class DichVu(db.Model):
    ma_dv = Column(String(20), primary_key=True)
    ten_dich_vu = Column(String(80), nullable=False)
    don_gia = Column(Double, nullable=False)

    phieu_dieu_tri = relationship(
        "PhieuDieuTri",
        back_populates="dich_vu",
        cascade="all, delete-orphan"
    )
    lich_hen = relationship(
        "LichHen",
        back_populates="dich_vu",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<MaDichVu: {self.ma_dv}>"

    def __str__(self):
        return f"<DichVu: {self.ten_dich_vu}>"


class PhieuDieuTri(BaseModel):
    # ma_phieu_dieu_tri = super().id

    ho_so_benh_nhan_id = Column(String(20), ForeignKey(HoSoBenhNhan.ma_ho_so), nullable=False)
    dich_vu_id = Column(String(20), ForeignKey(DichVu.ma_dv), nullable=False)
    bac_si_id = Column(Integer, ForeignKey(BacSi.ma_bac_si), nullable=False)
    don_thuoc_id = Column(Integer, ForeignKey("don_thuoc.id"), nullable=False)

    ho_so_benh_nhan = relationship("HoSoBenhNhan", back_populates="phieu_dieu_tri")
    dich_vu = relationship("DichVu", back_populates="phieu_dieu_tri")
    bac_si = relationship("BacSi", back_populates="phieu_dieu_tri")

    def __repr__(self):
        return f"<MaPhieuDieuTri: {self.id}>"


class DonThuoc(BaseModel):
    phieu_dieu_tri_id = Column(
        Integer,
        ForeignKey(PhieuDieuTri.id, ondelete="CASCADE"),
        nullable=False,
        unique=True  # Moi phieu dieu tri chi co toi da 1 don thuoc
    )
    thuoc_id = Column(
        Integer,
        ForeignKey("thuoc.ma_thuoc", ondelete="CASCADE"),
        nullable=False,
        unique=True  # Moi phieu dieu tri chi co toi da 1 don thuoc
    )
    ngay_boc_thuoc = Column(DateTime)

    lieu_luong_su_dung = relationship("LieuLuongSuDung", back_populates="don_thuoc")

    def __repr__(self):
        return f"<DonThuoc {self.id} PDT:{self.phieu_dieu_tri_id}>"


class Thuoc(db.Model):
    ma_thuoc = db.Column(Integer, primary_key=True, autoincrement=True)
    ten_thuoc = db.Column(db.String(100), nullable=False)
    lieu_luong_su_dung = relationship("LieuLuongSuDung", back_populates="thuoc")
    lo_thuocs = relationship('LoThuoc', backref='thuoc', lazy=True)


class LoThuoc(BaseModel):
    han_su_dung = Column(DateTime, nullable=False)
    ngay_nhap = Column(DateTime, nullable=False)
    so_luong = Column(Integer, nullable=False)
    thuoc_id = Column(Integer, ForeignKey(Thuoc.ma_thuoc), nullable=False)


class LieuLuongSuDung(BaseModel):
    so_luong = Column(Integer, nullable=False)

    don_thuoc_id = Column(Integer, ForeignKey(DonThuoc.id, ondelete="CASCADE"), nullable=False)
    thuoc_id = Column(Integer, ForeignKey(Thuoc.ma_thuoc,  ondelete="CASCADE"), nullable=False)

    don_thuoc = relationship("DonThuoc", back_populates="lieu_luong_su_dung")
    thuoc = relationship("Thuoc", back_populates="lieu_luong_su_dung")

    def __repr__(self):
        return f"<LieuLuongSuDung Don:{self.don_thuoc_id} Thuoc:{self.thuoc_id} SL:{self.so_luong}>"


class HoaDon(BaseModel):
    pass

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        import hashlib
        u = [
             User(name='receptionist', user_role=UserRole.RECEPTIONIST, phone='0123456',
                  avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg',
                  username='receptionist', password=str(hashlib.md5("123456".encode('utf-8')).hexdigest())),
             User(name='cashier', user_role=UserRole.CASHIER, phone='01234567',
                  avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg',
                  username='cashier', password=str(hashlib.md5("123456".encode('utf-8')).hexdigest())),
             User(name='user', user_role=UserRole.USER, phone='0123456',
                  avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg',
                  username='User', password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()))
             ]
        for user in u:
            db.session.add(user)
        db.session.commit()