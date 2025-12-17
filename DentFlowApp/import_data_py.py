import json
import hashlib
from datetime import datetime, timedelta
from DentFlowApp import app, db
from DentFlowApp.models import (
    NguoiDung, UserRole, GioiTinh, LoaiBacSi, TrangThaiLamViec,
    NhanVien, BacSi, BacSiFullTime, BacSiPartTime,
    Thuoc, LoThuoc, DichVu, HoSoBenhNhan,
    LichLamViec, LichHen, PhieuDieuTri, HoaDon, DonThuoc, LieuLuongSuDung
)


def hash_pass(p):
    return str(hashlib.md5(p.strip().encode('utf-8')).hexdigest())


def get_date_offset(days=0):
    return datetime.now().date() + timedelta(days=days)


def get_time_obj(time_str):
    return datetime.strptime(time_str, '%H:%M').time()


def import_all_data():
    try:
        with open('./mock/data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Không tìm thấy file data.json!")
        return

    # 1. Reset Database
    db.drop_all()
    db.create_all()
    print("--- Đã làm mới Database ---")

    map_users = {}  # username -> User Object
    map_services = {}  # ten_dich_vu -> Service Object
    map_medicines = {}  # ten_thuoc -> Medicine Object

    # Map username -> HoSoBenhNhan Object (để dễ tra cứu khi tạo lịch hẹn)
    map_patient_by_username = {}

    # 2. Users (Tạo user trước để lấy ID)
    print("Đang import Users...")
    for u in data.get('users', []):
        # Chuyển đổi string sang Enum
        role_enum = getattr(UserRole, u['vai_tro'])
        gender_enum = getattr(GioiTinh, u['gioi_tinh']) if u.get('gioi_tinh') else None

        user = NguoiDung(
            username=u['username'],
            password=hash_pass(u['password']),
            ho_ten=u['ho_ten'],
            vai_tro=role_enum,
            so_dien_thoai=u['so_dien_thoai'],
            gioi_tinh=gender_enum,
            avatar=u.get('avatar')
        )
        db.session.add(user)
        map_users[u['username']] = user

    # Commit để user có ID ngay lập tức
    db.session.commit()

    # 3. Nhân viên (Liên kết User)
    print("Đang import Nhân viên...")
    for s in data.get('staffs', []):
        u_acc = map_users.get(s['username_lien_ket'])
        if u_acc:
            nv = NhanVien(
                ma_nv=s['ma_nv'],
                # Không còn ho_ten, so_dien_thoai ở đây nữa
                dia_chi=s['dia_chi'],
                muc_luong=s['muc_luong'],
                nam_sinh=s.get('nam_sinh'),
                ngay_vao_lam=datetime.now(),
                nguoi_dung_id=u_acc.id
            )
            db.session.add(nv)

    # 4. Bác sĩ (Liên kết User)
    print("Đang import Bác sĩ...")
    for d in data.get('doctors', []):
        u_acc = map_users.get(d['username_lien_ket'])
        if u_acc:
            loai = getattr(LoaiBacSi, d['loai_bac_si'])
            bs = BacSi(
                ma_bac_si=d['ma_bac_si'],
                # Không còn ho_ten, so_dien_thoai ở đây nữa
                loai_bac_si=loai,
                nguoi_dung_id=u_acc.id
            )
            db.session.add(bs)

            if loai == LoaiBacSi.TOAN_THOI_GIAN:
                db.session.add(BacSiFullTime(ma_bac_si=d['ma_bac_si'], luong_co_ban=d.get('luong_co_ban')))
            else:
                db.session.add(BacSiPartTime(ma_bac_si=d['ma_bac_si'], muc_luong_gio=d.get('muc_luong_gio')))

    # 5. Bệnh nhân (Liên kết User)
    print("Đang import Bệnh nhân...")
    for p in data.get('patients', []):
        u_acc = map_users.get(p['username_lien_ket'])
        if u_acc:
            # Model HoSoBenhNhan giờ chỉ còn dia_chi và nguoi_dung_id
            bn = HoSoBenhNhan(
                dia_chi=p['dia_chi'],
                nguoi_dung_id=u_acc.id
            )
            db.session.add(bn)
            # Lưu vào map để lát dùng tạo lịch hẹn
            map_patient_by_username[p['username_lien_ket']] = bn

    # 6. Dịch vụ & Thuốc (Không thay đổi nhiều)
    print("Đang import Dịch vụ & Thuốc...")
    for sv in data.get('services', []):
        obj = DichVu(ten_dich_vu=sv['ten_dich_vu'], don_gia=sv['don_gia'])
        db.session.add(obj)
        map_services[sv['ten_dich_vu']] = obj

    for m in data.get('medicines', []):
        obj = Thuoc(ten_thuoc=m['ten_thuoc'])
        db.session.add(obj)
        map_medicines[m['ten_thuoc']] = obj
        db.session.flush()

        for b in m.get('batches', []):
            lt = LoThuoc(
                han_su_dung=datetime.now() + timedelta(days=b['han_dung_ngay']),
                so_luong=b['so_luong'],
                thuoc_id=obj.id
            )
            db.session.add(lt)

    # 7. Lịch làm việc
    print("Đang import Lịch làm việc...")
    for sch in data.get('schedules', []):
        llv = LichLamViec(
            ngay_lam=get_date_offset(sch['ngay_offset']),
            gio_bat_dau=get_time_obj(sch['gio_bat_dau']),
            gio_ket_thuc=get_time_obj(sch['gio_ket_thuc']),
            trang_thai=getattr(TrangThaiLamViec, sch['trang_thai']),
            bac_si_id=sch['ma_bac_si']
        )
        db.session.add(llv)

    # 8. Lịch hẹn
    print("Đang import Lịch hẹn...")
    for appt in data.get('appointments', []):
        # Tra cứu hồ sơ bệnh nhân qua username đã lưu ở bước 5
        p_obj = map_patient_by_username.get(appt['patient_username'])
        s_obj = map_services.get(appt['service_name'])

        if p_obj and s_obj:
            lh = LichHen(
                ngay_dat=datetime.now(),
                gio_kham=get_time_obj(appt['gio_kham']),
                ho_so_benh_nhan_id=p_obj.id,
                bac_si_id=appt['ma_bac_si'],
                dich_vu_id=s_obj.id
            )
            db.session.add(lh)

    db.session.commit()
    print("--- HOÀN TẤT IMPORT TOÀN BỘ DỮ LIỆU ---")
    print("Admin: admin/123")
    print("Bác sĩ A: bacsi_a/123")
    print("Bệnh nhân A: benhnhan_a/123")


if __name__ == '__main__':
    with app.app_context():
        import_all_data()
