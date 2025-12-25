from datetime import datetime, timedelta
from DentFlowApp.models import LichHen, Thuoc, UserRole, LoThuoc
from DentFlowApp import db
from flask_login import current_user
from DentFlowApp.admin import admin
from DentFlowApp.dao import thuoc_dao
from datetime import date, datetime, timedelta

import re


def user_can_do(User):
    can_do = {}
    if User.vai_tro == UserRole.USER:
        can_do['Hồ sơ của tôi'] = '/user'
        can_do['Lịch hẹn của tôi'] = '#'
    if User.vai_tro == UserRole.RECEPTIONIST:
        can_do['Trang lễ tân'] = '/receptionist'
    if User.vai_tro == UserRole.CASHIER:
        can_do['Trang thu ngân'] = '/cashier'
    if User.vai_tro == UserRole.MANAGER:
        can_do['Trang quản lý'] = '/manager'
    if User.vai_tro == UserRole.DOCTOR:
        can_do['Trang bác sĩ'] = '/treatment'
    # else:
    #     for item in admin.menu():
    #         if item.is_accessible():
    #             if item.name != 'Home' and item.name != 'Đăng xuất':
    #                 can_do[item.name] = item.get_url()
    return can_do


class ValidationUtils:
    @staticmethod
    def tim_lo_thuoc_tot_nhat(thuoc_id, so_ngay_dung):
        try:
            lo_phu_hop = thuoc_dao.get_lo_thuoc_phu_hop(thuoc_id, so_ngay_dung)

            if lo_phu_hop:
                return True, lo_phu_hop, "Tìm thấy lô thuốc phù hợp."

            lo_xa_nhat = thuoc_dao.get_lo_co_han_xa_nhat(thuoc_id)

            if not lo_xa_nhat:
                return False, None, "Thuốc này đã hết hàng hoặc hết hạn sử dụng."

            ngay_hien_tai = datetime.now().date()
            han_su_dung_date = lo_xa_nhat.han_su_dung
            if isinstance(han_su_dung_date, datetime):
                han_su_dung_date = han_su_dung_date.date()

            so_ngay_toi_da = (han_su_dung_date - ngay_hien_tai).days
            if so_ngay_toi_da < 0:
                return False, None, "Thuốc đã hết hạn."

            return False, None, f"Không có lô đủ hạn. Lô tốt nhất chỉ dùng được tối đa {so_ngay_toi_da} ngày."

        except Exception as e:
            return False, None, str(e)


class CalculationUtils:
    @staticmethod
    def tinh_tong_hoa_don(tien_dich_vu, danh_sach_thuoc):

        tong_tien_thuoc = 0

        for item in danh_sach_thuoc:
            t = Thuoc.query.get(item['id'])
            if t:
                tong_tien_thuoc += t.gia * item['so_luong']

        VAT_RATE = 0.10
        tong_chua_vat = tien_dich_vu + tong_tien_thuoc
        tien_vat = tong_chua_vat * VAT_RATE
        tong_thanh_toan = tong_chua_vat + tien_vat

        return {
            "tien_dich_vu": tien_dich_vu,
            "tien_thuoc": tong_tien_thuoc,
            "vat": tien_vat,
            "tong_thanh_toan": tong_thanh_toan
        }


def validate_thong_tin_benh_nhan(ho_ten, sdt, email=None, password=None, confirm_password=None):
    ho_ten = ho_ten.strip() if ho_ten else ""
    sdt = sdt.strip() if sdt else ""
    email = email.strip() if email else ""

    if not ho_ten:
        return False, "Họ tên không được để trống."

    if any(char.isdigit() for char in ho_ten):
        return False, "Họ tên không được chứa số."

    if not re.match(r"^0\d{9}$", sdt):
        return False, "Số điện thoại phải gồm 10 chữ số và bắt đầu bằng số 0."

    if email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Email không đúng định dạng."
    if password:
        if len(password) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự."

        if ' ' in password:
            return False, "Mật khẩu không được chứa khoảng trắng."

        if confirm_password is not None and password != confirm_password:
            return False, "Mật khẩu xác nhận không khớp."
    return True, None


def validate_booking(doctor_id, booking_date, time_slot, doctor_name):
    doctor_id = doctor_id.strip() if doctor_id else ""
    doctor_name = doctor_name.strip() if doctor_name else ""
    booking_date = booking_date.strip() if booking_date else ""
    time_slot = time_slot.strip() if time_slot else ""
    if not doctor_id:
        return False, "Không nhân được id của bác sĩ"

    if not doctor_name:
        return False, "Không nhân được tên của bác sĩ"

    if not booking_date:
        return False, "Không nhân được của ngày đặt lịch"

    if not time_slot:
        return False, "chưa giờ đặt"
    return True, None


def get_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def get_sunday(monday: date) -> date:
    return monday + timedelta(days=6)


def get_week_dates(monday: date):
    return [monday + timedelta(days=i) for i in range(7)]
