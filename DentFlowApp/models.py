from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Enum as sqlEnum, DateTime, Date, Time, Double, ForeignKey, Float, \
    Boolean
from sqlalchemy.orm import relationship
from DentFlowApp import db, app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum


# ENUMS

class GioiTinh(enum.Enum):
    NAM = "Nam"
    NU = "Nữ"
    KHAC = "Khác"


class DonViThuoc(enum.Enum):
    VIEN = "viên"
    VI = "vỉ"
    ONG = "ống"
    CHAI = "chai"
    GOI = "gói"
    HOP = "hộp"


class UserRole(enum.Enum):
    ADMIN = 1
    USER = 2
    RECEPTIONIST = 3
    DOCTOR = 4
    CASHIER = 5
    MANAGER = 6


class TrangThaiLamViec(enum.Enum):
    DANG_BAN = "Đang bận"
    SAN_SANG = "Sẵn sàng"
    NGHI = "Nghỉ"


class TrangThaiLichHen(enum.Enum):
    DAT_LICH_THANH_CONG = "Đặt lịch thành công"
    CHO_KHAM = "Chờ khám"
    DA_KHAM = "Đã khám"
    HUY = "Hủy"


class LoaiBacSi(enum.Enum):
    TOAN_THOI_GIAN = "Toàn thời gian"
    BAN_THOI_GIAN = "Bán thời gian"


class TrangThaiThanhToan(enum.Enum):
    CHUA_THANH_TOAN = 1
    DA_THANH_TOAN = 2
    HOAN_TIEN = 3


class PhuongThucThanhToan(enum.Enum):
    TIEN_MAT = 1
    CHUYEN_KHOAN_VIETQR = 2
    CHUYEN_KHOAN_MOMO = 3


# MODELS
class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    ngay_tao = Column(DateTime, default=datetime.now())
    ngay_cap_nhat = Column(DateTime, onupdate=datetime.now(), default=datetime.now())
    dang_hoat_dong = Column(Boolean, default=True)


class NguoiDung(BaseModel, UserMixin):
    __tablename__ = 'nguoi_dung'
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    ho_ten = Column(String(100), nullable=False)
    so_dien_thoai = Column(String(15))
    avatar = Column(String(255))
    vai_tro = Column(sqlEnum(UserRole), default=UserRole.USER)

    # Lấy hồ sơ bênh nhân từ người dùng NguoiDung.ho_so_benh_nhan
    ho_so_benh_nhan = relationship('HoSoBenhNhan', backref='nguoi_dung', uselist=False)
    bac_si = relationship('BacSi', backref='nguoi_dung', uselist=False)


class NhanVien(db.Model):
    ma_nv = Column(String(5), primary_key=True)
    ho_ten = Column(String(100), nullable=False)
    ngay_sinh = Column(DateTime)
    nam_sinh = Column(Integer)
    so_dien_thoai = Column(String(15), nullable=False)
    dia_chi = Column(String(255), nullable=False)
    muc_luong = Column(Float)
    ngay_vao_lam = Column(DateTime, default=datetime.now())

    # Mỗi nhân viên có 1 tài khoản
    nguoi_dung_id = Column(Integer, ForeignKey(NguoiDung.id), nullable=True)


class HoSoBenhNhan(BaseModel):
    __tablename__ = 'ho_so_benh_nhan'
    ho_ten = Column(String(100), nullable=False)
    so_dien_thoai = Column(String(15), nullable=False)
    ngay_tao = Column(DateTime, default=datetime.now())
    dia_chi = Column(String(255), nullable=True)
    gioi_tinh = Column(sqlEnum(GioiTinh), nullable=True)
    email = Column(String(50), nullable=True)
    ngay_sinh = Column(Date, nullable=True)
    CCCD = Column(String(12), nullable=True)
    # Tài khoản của người dùng (Nếu có)
    nguoi_dung_id = Column(Integer, ForeignKey('nguoi_dung.id', ondelete='SET NULL'), nullable=True)

    # lịch hẹn và phiếu điều trị tra cứu từ hồ sơ
    lich_hen_ds = relationship('LichHen', backref='ho_so_benh_nhan', lazy=True, cascade="all, delete-orphan")
    phieu_dieu_tri_ds = relationship('PhieuDieuTri', backref='ho_so_benh_nhan', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'ho_ten': self.ho_ten,
            'so_dien_thoai': self.so_dien_thoai,
            'email': self.email or '',
            'ngay_sinh': self.ngay_sinh.strftime('%Y-%m-%d') if self.ngay_sinh else '',
            'gioi_tinh': self.gioi_tinh.name if self.gioi_tinh else '',
            'cccd': self.CCCD or '',
            'dia_chi': self.dia_chi or ''
        }


class BacSi(db.Model):
    __tablename__ = 'bac_si'
    ma_bac_si = Column(String(5), primary_key=True)  # Map với maBacSi
    ho_ten = Column(String(100), nullable=False)
    so_dien_thoai = Column(String(15))
    avatar = Column(String(255))
    loai_bac_si = Column(sqlEnum(LoaiBacSi))

    # Tài khoản của bác sĩ
    nguoi_dung_id = Column(Integer, ForeignKey(NguoiDung.id, ondelete='SET NULL'), nullable=True)

    # Lấy các lịch hẹn cũng như phiếu điều trị để phục vụ việc lọc thanh toán hay đặt lịch
    lich_lam_viec_ds = relationship('LichLamViec', backref='bac_si', lazy=True, cascade="all, delete-orphan")
    lich_hen_ds = relationship('LichHen', backref='bac_si', lazy=True)
    phieu_dieu_tri_ds = relationship('PhieuDieuTri', backref='bac_si', lazy=True)


class BacSiFullTime(db.Model):
    ma_bac_si = Column(String(5), ForeignKey(BacSi.ma_bac_si, ondelete='CASCADE'), primary_key=True)
    luong_co_ban = Column(Float, nullable=True)


class BacSiPartTime(db.Model):
    ma_bac_si = Column(String(5), ForeignKey(BacSi.ma_bac_si, ondelete='CASCADE'), primary_key=True)
    muc_luong_gio = Column(Float, nullable=True)


class LichLamViec(BaseModel):
    __tablename__ = 'lich_lam_viec'
    ngay_lam = db.Column(Date, nullable=False)
    gio_bat_dau = Column(Time, nullable=False)
    gio_ket_thuc = Column(Time, nullable=False)
    trang_thai = Column(sqlEnum(TrangThaiLamViec), default=TrangThaiLamViec.SAN_SANG)

    bac_si_id = Column(String(5), ForeignKey('bac_si.ma_bac_si', ondelete='CASCADE'), nullable=False)


class DichVu(BaseModel):
    __tablename__ = 'dich_vu'
    ten_dich_vu = Column(String(100), nullable=False)
    don_gia = Column(Float, nullable=False)

    lich_hen_ds = relationship('LichHen', backref='dich_vu', lazy=True)
    phieu_dieu_tri_ds = relationship('ChiTietPhieuDieuTri', backref='dich_vu', lazy=True)
    chi_tiet_dich_vu = relationship('ChiTietDichVu', backref='dich_vu', lazy=True, cascade="all, delete-orphan")


class ChiTietDichVu(db.Model):
    __tablename__ = 'chi_tiet_dich_vu'
    id = Column(Integer, ForeignKey(DichVu.id, ondelete='CASCADE'), primary_key=True)
    noi_dung_chi_tiet = Column(String(255), nullable=True)


class LichHen(BaseModel):
    __tablename__ = 'lich_hen'
    ngay_dat = Column(Date, default=datetime.now())
    gio_kham = Column(Time, nullable=False)

    ho_so_benh_nhan_id = Column(Integer, ForeignKey('ho_so_benh_nhan.id', ondelete='CASCADE'), nullable=False)

    bac_si_id = Column(String(5), ForeignKey('bac_si.ma_bac_si'), nullable=False)
    dich_vu_id = Column(Integer, ForeignKey('dich_vu.id', ondelete='RESTRICT'), nullable=True)
    trang_thai = Column(sqlEnum(TrangThaiLichHen), default=TrangThaiLichHen.DAT_LICH_THANH_CONG)

    ghi_chu = Column(String(100), nullable=True)


class PhieuDieuTri(BaseModel):
    __tablename__ = 'phieu_dieu_tri'
    ghi_chu = Column(String(255), nullable=True)
    chan_doan = Column(String(255), nullable=True)
    trang_thai_thanh_toan = Column(sqlEnum(TrangThaiThanhToan), nullable=False,
                                   default=TrangThaiThanhToan.CHUA_THANH_TOAN)
    ho_so_benh_nhan_id = Column(Integer, ForeignKey('ho_so_benh_nhan.id'), nullable=False)
    bac_si_id = Column(String(5), ForeignKey('bac_si.ma_bac_si'), nullable=False)
    # dich_vu_id = Column(Integer, ForeignKey('dich_vu.id'), nullable=False)

    hoa_don = relationship('HoaDon', backref='phieu_dieu_tri', uselist=False, cascade="all, delete-orphan")
    don_thuoc = relationship('DonThuoc', backref='phieu_dieu_tri', uselist=False, cascade="all, delete-orphan")

    chi_tiet_dich_vu = relationship('ChiTietPhieuDieuTri', backref='phieu_dieu_tri', lazy=True,
                                    cascade="all, delete-orphan")

    @property
    def get_tong_tien(self):
        tong_tien = 0
        if not self.chi_tiet_dich_vu:
            return 0
        for dich_vu in self.chi_tiet_dich_vu:
            tong_tien += dich_vu.don_gia
        if self.don_thuoc:
            for ct in self.don_thuoc.ds_thuoc:
                tong_tien += ct.thuoc.don_gia * ct.so_luong
        return tong_tien

    @property
    def get_ds_dich_vu(self):
        ds_dich_vu = list()
        for chi_tiet in self.chi_tiet_dich_vu:
            ds_dich_vu.append(chi_tiet)
        return ds_dich_vu


class ChiTietPhieuDieuTri(BaseModel):
    __tablename__ = 'chi_tiet_phieu_dieu_tri'
    phieu_dieu_tri_id = Column(Integer, ForeignKey('phieu_dieu_tri.id', ondelete='CASCADE'), nullable=False)
    dich_vu_id = Column(Integer, ForeignKey('dich_vu.id', ondelete='RESTRICT'), nullable=False)

    don_gia = Column(Integer, nullable=False)


class HoaDon(BaseModel):
    __tablename__ = 'hoa_don'
    tong_tien = Column(Float)
    ngay_thanh_toan = Column(DateTime, default=datetime.now())
    nhan_vien_id = Column(Integer, ForeignKey('nguoi_dung.id', ondelete='CASCADE'), nullable=False)
    phuong_thuc_thanh_toan = Column(sqlEnum(PhuongThucThanhToan), nullable=False)
    phieu_dieu_tri_id = Column(Integer, ForeignKey('phieu_dieu_tri.id', ondelete='CASCADE'), nullable=False,
                               unique=True)


class Thuoc(BaseModel):
    __tablename__ = 'thuoc'
    ten_thuoc = Column(String(100), nullable=False)
    don_vi = Column(sqlEnum(DonViThuoc), nullable=False, default=DonViThuoc.VIEN)
    cac_lo_thuoc = relationship('LoThuoc', backref='thuoc', lazy=True, cascade="all, delete-orphan")
    don_gia = Column(Float, nullable=False)


class LoThuoc(db.Model):
    __tablename__ = 'lo_thuoc'
    id = Column(Integer, primary_key=True)
    han_su_dung = Column(DateTime, nullable=False)
    so_luong = Column(Integer, nullable=False)
    ngay_nhap = Column(DateTime, default=datetime.now())

    thuoc_id = Column(Integer, ForeignKey('thuoc.id', ondelete='CASCADE'), nullable=False)


class DonThuoc(BaseModel):
    __tablename__ = 'don_thuoc'
    ngay_boc_thuoc = Column(DateTime, default=datetime.now())
    phieu_dieu_tri_id = Column(Integer, ForeignKey('phieu_dieu_tri.id', ondelete='CASCADE'), nullable=False,
                               unique=True)
    ds_thuoc = relationship('LieuLuongSuDung', backref='don_thuoc_ref', lazy=True, cascade="all, delete-orphan")


# Bảng trung gian giữa đơn thuốc và thuốc cho biết liều lượng
class LieuLuongSuDung(BaseModel):
    __tablename__ = 'lieu_luong_su_dung'
    don_thuoc_id = Column(Integer, ForeignKey('don_thuoc.id', ondelete='CASCADE'))
    thuoc_id = Column(Integer, ForeignKey('thuoc.id', ondelete='RESTRICT'))

    thuoc = relationship('Thuoc', backref='cac_lieu_luong', lazy=True)

    so_luong = Column(Integer, nullable=False)
    huong_dan = Column(String(255))

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         # import hashlib
#         # u = [
#         #      NguoiDung(ho_ten='receptionist', vai_tro=UserRole.RECEPTIONIST, so_dien_thoai='0123456',
#         #           avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg',
#         #           username='receptionist', password=str(hashlib.md5("123456".encode('utf-8')).hexdigest())),
#         #     NguoiDung(ho_ten='cashier', vai_tro=UserRole.CASHIER, so_dien_thoai='0123456',
#         #               avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg',
#         #               username='cashier', password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()))
#         #     ,
#         #     NguoiDung(ho_ten='user', vai_tro=UserRole.USER, so_dien_thoai='0123456',
#         #               avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg',
#         #               username='user', password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()))
#         #      ]
#         # for user in u:
#         #     db.session.add(user)
#         # db.session.commit()
