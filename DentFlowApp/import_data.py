import json
import hashlib
from datetime import datetime, timedelta
from DentFlowApp import app, db, bcrypt

# 1. CẬP NHẬT IMPORT: Thêm PhuongThucThanhToan
from DentFlowApp.models import (
    NguoiDung, UserRole, GioiTinh, LoaiBacSi,
    BacSi, BacSiFullTime, BacSiPartTime,
    Thuoc, LoThuoc, DichVu, HoSoBenhNhan, LichHen,
    TrangThaiLichHen, LichLamViec, TrangThaiLamViec,
    DonViThuoc, ChiTietPhieuDieuTri, HoaDon, PhieuDieuTri,
    TrangThaiThanhToan, PhuongThucThanhToan  # <-- Quan trọng
)


def hash_pass(password):
    return bcrypt.generate_password_hash(password.strip()).decode('utf-8')


def import_json_data():
    try:
        with open('./mock/data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file data.json")
        return

    # Reset Database
    db.drop_all()
    db.create_all()
    print("--- Đã reset database ---")

    user_map = {}
    service_map = {}
    patient_map = {}
    service_price_map = {}
    cashier_id = None  # Lưu ID thu ngân để gán vào hóa đơn

    # 1. Import Users
    print("1. Đang import Users...")
    for u in data.get('users', []):
        user = NguoiDung(
            username=u['username'],
            password=hash_pass(u['password']),
            ho_ten=u['ho_ten'],
            vai_tro=getattr(UserRole, u['vai_tro']),
            so_dien_thoai=u['so_dien_thoai'],
            avatar=u['avatar']
        )
        db.session.add(user)
        db.session.flush()
        user_map[u['username']] = user

        # Tìm một thu ngân để gán mặc định cho hóa đơn
        if user.vai_tro == UserRole.CASHIER and cashier_id is None:
            cashier_id = user.id

    # 2. Import Bác sĩ
    print("2. Đang import Bác sĩ...")
    for d in data.get('doctors', []):
        loai_enum = getattr(LoaiBacSi, d['loai_bac_si'])
        u_account = user_map.get(d['username_lien_ket'])

        doctor = BacSi(
            ma_bac_si=d['ma_bac_si'],
            ho_ten=d['ho_ten'],
            so_dien_thoai=d['so_dien_thoai'],
            loai_bac_si=loai_enum,
            nguoi_dung_id=u_account.id if u_account else None
        )
        db.session.add(doctor)

        if loai_enum == LoaiBacSi.TOAN_THOI_GIAN:
            dt = BacSiFullTime(ma_bac_si=d['ma_bac_si'], luong_co_ban=d.get('luong_co_ban'))
            db.session.add(dt)
        else:
            dt = BacSiPartTime(ma_bac_si=d['ma_bac_si'], muc_luong_gio=d.get('muc_luong_gio'))
            db.session.add(dt)

    # 3. Import Dịch vụ
    print("3. Đang import Dịch vụ...")
    for s in data.get('services', []):
        sv = DichVu(ten_dich_vu=s['ten_dich_vu'], don_gia=s['don_gia'])
        db.session.add(sv)
        db.session.flush()
        service_map[s['ten_dich_vu']] = sv.id
        service_price_map[s['ten_dich_vu']] = s['don_gia']

    # 4. Import Thuốc
    print("4. Đang import Thuốc...")
    for m in data.get('medicines', []):
        don_vi_enum = getattr(DonViThuoc, m['don_vi'])
        thuoc = Thuoc(ten_thuoc=m['ten_thuoc'], don_vi=don_vi_enum)
        db.session.add(thuoc)
        db.session.flush()

        for b in m.get('batches', []):
            lt = LoThuoc(
                han_su_dung=datetime.now() + timedelta(days=b['han_dung_ngay']),
                so_luong=b['so_luong'],
                thuoc_id=thuoc.id
            )
            db.session.add(lt)

    # 5. Import Bệnh nhân
    print("5. Đang import Bệnh nhân...")
    for p in data.get('patients', []):
        bn = HoSoBenhNhan(
            ho_ten=p['ho_ten'],
            so_dien_thoai=p['so_dien_thoai'],
            gioi_tinh=getattr(GioiTinh, p['gioi_tinh']),
            dia_chi=p['dia_chi'],
            ngay_sinh=datetime.strptime(p["ngay_sinh"], "%Y-%m-%d").date()
        )
        db.session.add(bn)
        db.session.flush()
        patient_map[p['so_dien_thoai']] = bn.id

    db.session.commit()

    # 6. Import Lịch hẹn
    print("6. Đang import Lịch hẹn...")
    for apt in data.get('appointments', []):
        bn_id = patient_map.get(apt['benh_nhan_sdt'])
        dv_id = service_map.get(apt['dich_vu_ten'])

        if bn_id and dv_id:
            try:
                ngay = datetime.strptime(apt['ngay_dat'], '%Y-%m-%d').date()
                gio = datetime.strptime(apt['gio_kham'], '%H:%M').time()

                lich_hen = LichHen(
                    ngay_dat=ngay,
                    gio_kham=gio,
                    ho_so_benh_nhan_id=bn_id,
                    bac_si_id=apt['bac_si_id'],
                    dich_vu_id=dv_id,
                    trang_thai=getattr(TrangThaiLichHen, apt['trang_thai']),
                    ghi_chu=apt.get('ghi_chu', '')
                )
                db.session.add(lich_hen)
            except ValueError as e:
                print(f"Lỗi format ngày giờ cho lịch hẹn: {e}")

    db.session.commit()

    # 7. Import Lịch làm việc
    print("7. Đang import Lịch làm việc...")
    for ws in data.get('work_schedules', []):
        try:
            ngay = datetime.strptime(ws['ngay_lam'], '%Y-%m-%d').date()
            bat_dau = datetime.strptime(ws['gio_bat_dau'], '%H:%M:%S').time()
            ket_thuc = datetime.strptime(ws['gio_ket_thuc'], '%H:%M:%S').time()

            lich_truc = LichLamViec(
                ngay_lam=ngay,
                gio_bat_dau=bat_dau,
                gio_ket_thuc=ket_thuc,
                bac_si_id=ws['bac_si_id'],
                trang_thai=getattr(TrangThaiLamViec, ws['trang_thai'])
            )
            db.session.add(lich_truc)
        except Exception as e:
            print(f"Lỗi import lịch trực: {e}")

    # 8. Import Phiếu Điều Trị & Hóa Đơn
    print("8. Đang import Phiếu Điều Trị & Hóa Đơn...")
    for trt in data.get('treatments', []):
        bn_id = patient_map.get(trt['benh_nhan_sdt'])
        if bn_id:
            try:
                # 8.1 Xử lý trạng thái thanh toán
                json_status = trt.get('trang_thai_thanh_toan', 'CHUA_THANH_TOAN')
                payment_status_enum = getattr(TrangThaiThanhToan, json_status)

                # Parse ngày tạo từ JSON (Đây là dữ liệu lịch sử)
                ngay_tao_lich_su = datetime.strptime(trt['ngay_tao'], '%Y-%m-%d %H:%M:%S')

                # 8.2 Tạo Phiếu Điều Trị
                pdt = PhieuDieuTri(
                    chan_doan=trt['chan_doan'],
                    ghi_chu=trt.get('ghi_chu', ''),
                    ho_so_benh_nhan_id=bn_id,
                    bac_si_id=trt['bac_si_id'],
                    ngay_tao=ngay_tao_lich_su,  # Quan trọng: Gán ngày cũ cho phiếu
                    trang_thai_thanh_toan=payment_status_enum
                )
                db.session.add(pdt)
                db.session.flush()

                # 8.3 Tạo chi tiết dịch vụ và tính tổng tiền
                tong_tien = 0
                for dv_ten in trt['dich_vu_su_dung']:
                    dv_id = service_map.get(dv_ten)
                    don_gia = service_price_map.get(dv_ten, 0)

                    if dv_id:
                        ct_pdt = ChiTietPhieuDieuTri(
                            phieu_dieu_tri_id=pdt.id,
                            dich_vu_id=dv_id,
                            don_gia=don_gia,
                            ngay_tao=ngay_tao_lich_su  # Gán ngày cũ cho chi tiết (nếu model có dùng)
                        )
                        db.session.add(ct_pdt)
                        tong_tien += don_gia

                # 8.4 Tạo hóa đơn CHỈ KHI trạng thái là ĐÃ THANH TOÁN
                if payment_status_enum == TrangThaiThanhToan.DA_THANH_TOAN:
                    # Lấy phương thức thanh toán từ JSON (mặc định TIEN_MAT)
                    method_str = trt.get('phuong_thuc_thanh_toan', 'TIEN_MAT')
                    method_enum = getattr(PhuongThucThanhToan, method_str)

                    if cashier_id:
                        # Giả lập thời gian thanh toán là 30 phút sau khi tạo phiếu
                        thoi_gian_thanh_toan = ngay_tao_lich_su + timedelta(minutes=30)

                        hoa_don = HoaDon(
                            tong_tien=tong_tien,
                            phieu_dieu_tri_id=pdt.id,
                            phuong_thuc_thanh_toan=method_enum,
                            nhan_vien_id=cashier_id,

                            # --- SỬA LỖI TẠI ĐÂY ---
                            # Truyền tham số ngay_tao để override default=datetime.now()
                            ngay_tao=thoi_gian_thanh_toan,  # Ngày tạo hóa đơn trong DB
                            ngay_thanh_toan=thoi_gian_thanh_toan  # Ngày thanh toán thực tế
                        )
                        db.session.add(hoa_don)
                    else:
                        print("Cảnh báo: Không tìm thấy nhân viên CASHIER để gán cho hóa đơn!")

            except Exception as e:
                print(f"Lỗi import phiếu điều trị: {e}")
    db.session.commit()
    print("--- Hoàn tất import dữ liệu! ---")


if __name__ == '__main__':
    with app.app_context():
        import_json_data()
