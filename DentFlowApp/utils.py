from datetime import datetime
from DentFlowApp.models import LichHen, Thuoc, UserRole
from DentFlowApp import db
from flask_login import current_user
from DentFlowApp.admin import admin

def user_can_do(User):
    can_do = {}
    if User.vai_tro == UserRole.USER:
        can_do['Hồ sơ của tôi'] = '#'
        can_do['Lịch hẹn của tôi'] = '#'
    else:
        for item in admin.menu():
            if item.is_accessible():
                if item.name != 'Home' and item.name != 'Đăng xuất':
                    can_do[item.name] = item.get_url()
    return can_do


class ValidationUtils:
    @staticmethod
    def check_lich_kham_hop_le(bac_si_id, ngay_kham_str, gio_kham_str):
        """
        Kiểm tra Yêu cầu 1:
        - Mỗi bác sĩ tối đa 5 lịch/ngày.
        - Không trùng giờ.
        """
        try:
            # Chuyển đổi string ngày thành object date (giả sử format form gửi lên là YYYY-MM-DD)
            ngay_kham = datetime.strptime(ngay_kham_str, '%Y-%m-%d').date()
        except ValueError:
            return False, "Định dạng ngày không hợp lệ."

        # 1. Kiểm tra số lượng lịch trong ngày
        count_lich = LichHen.query.filter(
            LichHen.bac_si_id == bac_si_id,
            LichHen.ngay_kham == ngay_kham
        ).count()

        if count_lich >= 5:
            return False, "Bác sĩ đã kín lịch (Tối đa 5 ca/ngày)."

        # 2. Kiểm tra trùng giờ
        bi_trung = LichHen.query.filter(
            LichHen.bac_si_id == bac_si_id,
            LichHen.ngay_kham == ngay_kham,
            LichHen.gio_kham == gio_kham_str
        ).first()

        if bi_trung:
            return False, f"Giờ {gio_kham_str} đã có người đặt."

        return True, "Hợp lệ"

    @staticmethod
    def check_thuoc_ke_don(thuoc_id):
        """
        Kiểm tra Yêu cầu 3:
        - Không kê thuốc quá hạn.
        - Thuốc phải nằm trong danh mục được phép.
        """
        thuoc = Thuoc.query.get(thuoc_id)
        if not thuoc:
            return False, "Thuốc không tồn tại."

        # Kiểm tra danh mục cho phép
        if not thuoc.is_allowed:
            return False, f"Thuốc {thuoc.ten_thuoc} không nằm trong danh mục được phép."

        # Kiểm tra hạn sử dụng
        if thuoc.ngay_he_han < datetime.now().date():
            return False, f"Thuốc {thuoc.ten_thuoc} đã hết hạn sử dụng (Hạn: {thuoc.ngay_he_han})."

        return True, "Thuốc hợp lệ."


class CalculationUtils:
    @staticmethod
    def tinh_tong_hoa_don(tien_dich_vu, danh_sach_thuoc):
        """
        Thực hiện Yêu cầu 4: Tính tổng chi phí
        danh_sach_thuoc: list các dict [{'id': 1, 'so_luong': 2}, ...]
        """
        tong_tien_thuoc = 0

        # Tính tiền thuốc
        for item in danh_sach_thuoc:
            t = Thuoc.query.get(item['id'])
            if t:
                tong_tien_thuoc += t.gia * item['so_luong']

        # Tính VAT 10%
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