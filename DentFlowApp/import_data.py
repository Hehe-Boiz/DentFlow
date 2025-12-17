import json
import hashlib
from datetime import datetime, timedelta
from DentFlowApp import app, db
from DentFlowApp.models import (
    NguoiDung, UserRole, GioiTinh, LoaiBacSi, TrangThaiLamViec,
    NhanVien, BacSi, BacSiFullTime, BacSiPartTime,
    Thuoc, LoThuoc, DichVu, HoSoBenhNhan,
    LichLamViec, LichHen
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
        print("Lỗi: Không tìm thấy file data.json!")
        return

    # 1. Reset Database
    db.drop_all()
    db.create_all()
    print("--- Đã làm mới Database ---")

    map_users = {}  # username -> User Object
    map_services = {}  # ten_dich_vu -> Service Object
    map_patients = {}  # so_dien_thoai -> HoSoBenhNhan Object

    # 2. Import Users
    print("Đang import Users...")
    for u in data.get('users', []):
        role_enum = getattr(UserRole, u['vai_tro'])

        # NguoiDung không còn trường gioi_tinh
        user = NguoiDung(
            username=u['username'],
            password=hash_pass(u['password']),
            ho_ten=u['ho_ten'],
            vai_tro=role_enum,
            so_dien_thoai=u['so_dien_thoai'],
            avatar=u.get('avatar')
        )
        db.session.add(user)
        map_users[u['username']] = user

    db.session.commit()

    # 3. Import Nhân viên
    print("Đang import Nhân viên...")
    for s in data.get('staffs', []):
        u_acc = map_users.get(s.get('username_lien_ket'))
        nv = NhanVien(
            ma_nv=s['ma_nv'],
            ho_ten=s['ho_ten'],
            so_dien_thoai=s['so_dien_thoai'],
            dia_chi=s['dia_chi'],
            muc_luong=s['muc_luong'],
            nam_sinh=s.get('nam_sinh'),
            ngay_vao_lam=datetime.now(),
            nguoi_dung_id=u_acc.id if u_acc else None
        )
        db.session.add(nv)

    # 4. Import Bác sĩ
    print("Đang import Bác sĩ...")
    for d in data.get('doctors', []):
        loai = getattr(LoaiBacSi, d['loai_bac_si'])
        u_acc = map_users.get(d.get('username_lien_ket'))
        bs = BacSi(
            ma_bac_si=d['ma_bac_si'],
            ho_ten=d['ho_ten'],
            so_dien_thoai=d['so_dien_thoai'],
            loai_bac_si=loai,
            nguoi_dung_id=u_acc.id if u_acc else None
        )
        db.session.add(bs)

        if loai == LoaiBacSi.TOAN_THOI_GIAN:
            db.session.add(BacSiFullTime(ma_bac_si=d['ma_bac_si'], luong_co_ban=d.get('luong_co_ban')))
        else:
            db.session.add(BacSiPartTime(ma_bac_si=d['ma_bac_si'], muc_luong_gio=d.get('muc_luong_gio')))

    # 5. Import Hồ sơ bệnh nhân (Có giới tính ở đây)
    print("Đang import Hồ sơ bệnh nhân...")
    for p in data.get('patients', []):
        u_acc = map_users.get(p.get('username_lien_ket'))
        # Giới tính nằm ở bảng HoSoBenhNhan
        gender_enum = getattr(GioiTinh, p['gioi_tinh'])

        bn = HoSoBenhNhan(
            ho_ten=p['ho_ten'],
            so_dien_thoai=p['so_dien_thoai'],
            gioi_tinh=gender_enum,
            dia_chi=p['dia_chi'],
            nguoi_dung_id=u_acc.id if u_acc else None
        )
        db.session.add(bn)
        map_patients[p['so_dien_thoai']] = bn

    db.session.commit()

    # 6. Import Dịch vụ & Thuốc
    print("Đang import Dịch vụ & Thuốc...")
    for sv in data.get('services', []):
        obj = DichVu(ten_dich_vu=sv['ten_dich_vu'], don_gia=sv['don_gia'])
        db.session.add(obj)
        map_services[sv['ten_dich_vu']] = obj

    for m in data.get('medicines', []):
        obj = Thuoc(ten_thuoc=m['ten_thuoc'])
        db.session.add(obj)
        db.session.flush()

        for b in m.get('batches', []):
            lt = LoThuoc(
                han_su_dung=datetime.now() + timedelta(days=b['han_dung_ngay']),
                so_luong=b['so_luong'],
                thuoc_id=obj.id
            )
            db.session.add(lt)

    # 7. Import Lịch làm việc
    print("Đang import Lịch làm việc...")
    for sch in data.get('schedules', []):
        trang_thai = getattr(TrangThaiLamViec, sch['trang_thai'])
        llv = LichLamViec(
            ngay_lam=get_date_offset(sch['ngay_offset']),
            gio_bat_dau=get_time_obj(sch['gio_bat_dau']),
            gio_ket_thuc=get_time_obj(sch['gio_ket_thuc']),
            trang_thai=trang_thai,
            bac_si_id=sch['ma_bac_si']
        )
        db.session.add(llv)

    # 8. Import Lịch hẹn
    print("Đang import Lịch hẹn...")
    for appt in data.get('appointments', []):
        p_obj = map_patients.get(appt['patient_phone'])
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
    print("--- HOÀN TẤT IMPORT DỮ LIỆU ---")


if __name__ == '__main__':
    with app.app_context():
        import_all_data()
