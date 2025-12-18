from datetime import datetime, timedelta, time
import random
from DentFlowApp import db, app
# Import các models cần thiết
from DentFlowApp.models import (
    HoSoBenhNhan, LichHen, BacSi, DichVu,
    GioiTinh, UserRole, NguoiDung
)


def create_patient_and_appointment_data():
    with app.app_context():
        print("--- Bắt đầu tạo dữ liệu Bệnh nhân & Lịch hẹn ---")

        # ---------------------------------------------------------
        # 1. TẠO DỮ LIỆU DỊCH VỤ (Cần có dịch vụ để đặt lịch)
        # ---------------------------------------------------------
        services_data = [
            {"ten": "Cạo vôi răng", "gia": 200000.0},
            {"ten": "Trám răng thẩm mỹ", "gia": 500000.0},
            {"ten": "Nhổ răng khôn", "gia": 1500000.0},
            {"ten": "Tẩy trắng răng", "gia": 1200000.0},
            {"ten": "Khám tổng quát", "gia": 100000.0}
        ]

        existing_services = DichVu.query.all()
        if not existing_services:
            print("Đang tạo danh sách Dịch vụ mẫu...")
            list_services = []
            for s in services_data:
                dv = DichVu(ten_dich_vu=s["ten"], don_gia=s["gia"])
                list_services.append(dv)
            db.session.add_all(list_services)
            db.session.commit()
            existing_services = list_services  # Cập nhật danh sách
        else:
            print(f"Đã có {len(existing_services)} dịch vụ.")

        # ---------------------------------------------------------
        # 2. TẠO HỒ SƠ BỆNH NHÂN (HoSoBenhNhan)
        # ---------------------------------------------------------
        print("Đang tạo Hồ sơ bệnh nhân...")

        # Danh sách tên mẫu
        last_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan"]
        middle_names = ["Văn", "Thị", "Đức", "Ngọc", "Thanh", "Minh"]
        first_names = ["An", "Bình", "Cường", "Dung", "Giang", "Hương", "Khánh", "Lan"]

        addresses = ["Hà Nội", "TP.HCM", "Đà Nẵng", "Cần Thơ", "Hải Phòng"]

        patients = []
        for i in range(10):  # Tạo 10 bệnh nhân
            # Random tên
            full_name = f"{random.choice(last_names)} {random.choice(middle_names)} {random.choice(first_names)}"

            # Random giới tính
            gender = random.choice([GioiTinh.NAM, GioiTinh.NU])

            bn = HoSoBenhNhan(
                ho_ten=full_name,
                so_dien_thoai=f"09{random.randint(10000000, 99999999)}",
                dia_chi=random.choice(addresses),
                gioi_tinh=gender,
                ngay_tao=datetime.now() - timedelta(days=random.randint(1, 365))  # Tạo trong vòng 1 năm qua
            )
            patients.append(bn)

        db.session.add_all(patients)
        db.session.commit()  # Commit để lấy ID cho bệnh nhân
        print(f"Đã tạo xong {len(patients)} hồ sơ bệnh nhân.")

        # ---------------------------------------------------------
        # 3. TẠO LỊCH HẸN (LichHen)
        # ---------------------------------------------------------
        print("Đang tạo Lịch hẹn...")

        doctors = BacSi.query.all()
        if not doctors:
            print("LỖI: Chưa có dữ liệu Bác sĩ. Vui lòng chạy script tạo Bác sĩ trước.")
            return

        appointments = []

        # Tạo lịch hẹn cho mỗi bệnh nhân (mỗi người 1-2 cuộc hẹn)
        for patient in patients:
            num_appts = random.randint(1, 2)

            for _ in range(num_appts):
                # Random ngày hẹn (từ hôm nay đến 7 ngày tới)
                days_ahead = random.randint(0, 7)
                appt_date = datetime.now() + timedelta(days=days_ahead)

                # Random giờ khám (08:00 - 17:00)
                hour = random.randint(8, 16)
                minute = random.choice([0, 30])
                appt_time = time(hour, minute)

                # Chọn random bác sĩ và dịch vụ
                doctor = random.choice(doctors)
                service = random.choice(existing_services)

                lh = LichHen(
                    ngay_dat=datetime.now(),  # Thời điểm đặt lịch là hiện tại
                    gio_kham=appt_time,  # Giờ khách đến khám
                    # Lưu ý: Model của bạn hiện tại LichHen chỉ có gio_kham,
                    # thường cần thêm ngay_hen (Date).
                    # Ở đây mình giả định logic đặt lịch dựa vào ngày tạo hoặc bạn sẽ update model sau.
                    # Tạm thời mình map data theo model hiện có.

                    ho_so_benh_nhan_id=patient.id,
                    bac_si_id=doctor.ma_bac_si,
                    dich_vu_id=service.id
                )
                appointments.append(lh)

        try:
            db.session.add_all(appointments)
            db.session.commit()
            print(f"Đã tạo thành công {len(appointments)} lịch hẹn!")
        except Exception as e:
            db.session.rollback()
            print(f"Có lỗi xảy ra khi tạo lịch hẹn: {str(e)}")


if __name__ == "__main__":
    create_patient_and_appointment_data()