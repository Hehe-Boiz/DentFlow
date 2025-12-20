import json
import hashlib
from datetime import datetime, timedelta
from DentFlowApp import app, db
from DentFlowApp.models import (
    NguoiDung, UserRole, GioiTinh, LoaiBacSi,
    BacSi, BacSiFullTime, BacSiPartTime,
    Thuoc, LoThuoc, DichVu, HoSoBenhNhan, LichHen,
    TrangThaiLichHen, LichLamViec, TrangThaiLamViec,
    DonViThuoc, ChiTietPhieuDieuTri, HoaDon, PhieuDieuTri
)


def hash_pass(password):
    return str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())


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

    # 1. Import Users
    print("Đang import Users...")
    for u in data.get('users', []):
        user = NguoiDung(
            username=u['username'],
            password=hash_pass(u['password']),
            ho_ten=u['ho_ten'],
            vai_tro=getattr(UserRole, u['vai_tro']),
            so_dien_thoai=u['so_dien_thoai'],  # Đã sửa khớp với model
            avatar=u['avatar']
        )
        db.session.add(user)
        db.session.flush()
        user_map[u['username']] = user

    # 2. Import Bác sĩ
    print("Đang import Bác sĩ...")
    for d in data.get('doctors', []):
        loai_enum = getattr(LoaiBacSi, d['loai_bac_si'])
        u_account = user_map.get(d['username_lien_ket'])

        doctor = BacSi(
            ma_bac_si=d['ma_bac_si'],
            ho_ten=d['ho_ten'],
            so_dien_thoai=d['so_dien_thoai'],  # Đã sửa khớp với model
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
    print("Đang import Dịch vụ...")
    for s in data.get('services', []):
        # Đã sửa khớp với model: ten_dich_vu, don_gia
        sv = DichVu(ten_dich_vu=s['ten_dich_vu'], don_gia=s['don_gia'])
        db.session.add(sv)
        db.session.flush()  # Flush để lấy ID ngay lập tức
        service_map[s['ten_dich_vu']] = sv.id
        service_price_map[s['ten_dich_vu']] = s['don_gia']

    # 4. Import Thuốc
    print("Đang import Thuốc...")
    for m in data.get('medicines', []):
        don_vi_enum = DonViThuoc[m['don_vi']]
        thuoc = Thuoc(ten_thuoc=m['ten_thuoc'], don_vi=don_vi_enum)  # Đã sửa khớp với model
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
    print("Đang import Bệnh nhân...")
    for p in data.get('patients', []):
        bn = HoSoBenhNhan(
            ho_ten=p['ho_ten'],
            so_dien_thoai=p['so_dien_thoai'],  # Đã sửa khớp với model
            gioi_tinh=getattr(GioiTinh, p['gioi_tinh']),
            dia_chi=p['dia_chi']
        )
        db.session.add(bn)
        db.session.flush()
        patient_map[p['so_dien_thoai']] = bn.id

    db.session.commit()

    # 6. Import Lịch hẹn (MỚI THÊM)
    print("Đang import Lịch hẹn...")
    for apt in data.get('appointments', []):
        # Tìm ID bệnh nhân qua SĐT
        bn_id = patient_map.get(apt['benh_nhan_sdt'])
        # Tìm ID dịch vụ qua tên
        dv_id = service_map.get(apt['dich_vu_ten'])

        if bn_id and dv_id:
            try:
                # Xử lý ngày giờ
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
        else:
            print(f"Không tìm thấy Bệnh nhân ({apt['benh_nhan_sdt']}) hoặc Dịch vụ ({apt['dich_vu_ten']})")

    db.session.commit()

    # 7. Import Lịch làm việc (MỚI THÊM)
    print("Đang import Lịch làm việc...")
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

    # 8. Import Phiếu Điều Trị & Hóa Đơn (MỚI)
    print("8. Đang import Phiếu Điều Trị & Hóa Đơn...")
    for trt in data.get('treatments', []):
        bn_id = patient_map.get(trt['benh_nhan_sdt'])
        if bn_id:
            try:
                # Tạo phiếu điều trị
                ngay_tao = datetime.strptime(trt['ngay_tao'], '%Y-%m-%d %H:%M:%S')
                pdt = PhieuDieuTri(
                    chan_doan=trt['chan_doan'],
                    ghi_chu=trt.get('ghi_chu', ''),
                    ho_so_benh_nhan_id=bn_id,
                    bac_si_id=trt['bac_si_id'],
                    ngay_tao=ngay_tao
                )
                db.session.add(pdt)
                db.session.flush()  # Để lấy ID phiếu điều trị

                # Tạo chi tiết dịch vụ và tính tổng tiền
                tong_tien = 0
                for dv_ten in trt['dich_vu_su_dung']:
                    dv_id = service_map.get(dv_ten)
                    don_gia = service_price_map.get(dv_ten, 0)

                    if dv_id:
                        ct_pdt = ChiTietPhieuDieuTri(
                            phieu_dieu_tri_id=pdt.id,
                            dich_vu_id=dv_id,
                            don_gia=don_gia
                        )
                        db.session.add(ct_pdt)
                        tong_tien += don_gia

                # Tạo hóa đơn nếu đã thanh toán
                if trt.get('da_thanh_toan', False):
                    hoa_don = HoaDon(
                        tong_tien=tong_tien,
                        ngay_thanh_toan=ngay_tao + timedelta(minutes=30),
                        phieu_dieu_tri_id=pdt.id
                    )
                    db.session.add(hoa_don)

            except Exception as e:
                print(f"Lỗi import phiếu điều trị: {e}")

    db.session.commit()
    print("--- Đã cập nhật lịch làm việc! ---")
    print("--- Hoàn tất import dữ liệu! ---")


if __name__ == '__main__':
    with app.app_context():
        import_json_data()
