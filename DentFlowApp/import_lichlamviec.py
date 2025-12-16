from datetime import datetime, timedelta, time
import random
from DentFlowApp import db, app
from DentFlowApp.models import BacSi, LichLamViec, TrangThaiLamViec, LoaiBacSi, GioiTinh


def create_fake_data():
    with app.app_context():
        print("--- Bắt đầu tạo dữ liệu giả ---")

        # 1. TẠO DỮ LIỆU BÁC SĨ (Cần có bác sĩ trước mới tạo được lịch)
        # Kiểm tra xem đã có bác sĩ chưa, nếu chưa thì tạo
        doctors = BacSi.query.all()

        if not doctors:
            print("Đang tạo dữ liệu Bác sĩ mẫu...")
            bs1 = BacSi(
                ma_bac_si="BS001",
                ho_ten="Nguyễn Văn A",
                so_dien_thoai="0901234567",
                loai_bac_si=LoaiBacSi.TOAN_THOI_GIAN
            )
            bs2 = BacSi(
                ma_bac_si="BS002",
                ho_ten="Trần Thị B",
                so_dien_thoai="0909876543",
                loai_bac_si=LoaiBacSi.BAN_THOI_GIAN
            )
            bs3 = BacSi(
                ma_bac_si="BS003",
                ho_ten="Lê Hoàng C",
                so_dien_thoai="0912345678",
                loai_bac_si=LoaiBacSi.TOAN_THOI_GIAN
            )

            db.session.add_all([bs1, bs2, bs3])
            db.session.commit()
            doctors = [bs1, bs2, bs3]  # Cập nhật danh sách để dùng bên dưới
        else:
            print(f"Đã tìm thấy {len(doctors)} bác sĩ hiện có.")

        # 2. TẠO DỮ LIỆU LỊCH LÀM VIỆC
        print("Đang tạo lịch làm việc cho 7 ngày tới...")

        today = datetime.now().date()
        schedules = []

        # Các trạng thái có thể xảy ra (Sẵn sàng chiếm tỉ lệ cao hơn)
        trang_thai_choices = [TrangThaiLamViec.SAN_SANG] * 8 + \
                             [TrangThaiLamViec.DANG_BAN] * 1 + \
                             [TrangThaiLamViec.NGHI] * 1

        for doctor in doctors:
            # Tạo lịch cho 7 ngày tới
            for i in range(7):
                current_day = today + timedelta(days=i)

                # Ca Sáng (08:00 - 12:00)
                ca_sang = LichLamViec(
                    ngay_lam=current_day,
                    gio_bat_dau=time(8, 0),
                    gio_ket_thuc=time(12, 0),
                    trang_thai=random.choice(trang_thai_choices),
                    bac_si_id=doctor.ma_bac_si
                )

                # Ca Chiều (13:30 - 17:30)
                ca_chieu = LichLamViec(
                    ngay_lam=current_day,
                    gio_bat_dau=time(13, 30),
                    gio_ket_thuc=time(17, 30),
                    trang_thai=random.choice(trang_thai_choices),
                    bac_si_id=doctor.ma_bac_si
                )

                schedules.append(ca_sang)
                schedules.append(ca_chieu)

        # Lưu vào DB
        try:
            db.session.add_all(schedules)
            db.session.commit()
            print(f"Đã thêm thành công {len(schedules)} bản ghi lịch làm việc!")
        except Exception as e:
            db.session.rollback()
            print(f"Có lỗi xảy ra: {str(e)}")


if __name__ == "__main__":
    create_fake_data()