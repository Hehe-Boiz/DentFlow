import json
import hashlib
from datetime import datetime, timedelta
from DentFlowApp import app, db
from DentFlowApp.models import (
    NguoiDung, UserRole, GioiTinh, LoaiBacSi,
    BacSi, BacSiFullTime, BacSiPartTime,
    Thuoc, LoThuoc, DichVu, HoSoBenhNhan
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
        user_map[u['username']] = user

    db.session.commit()

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

    # 4. Import Thuốc
    print("Đang import Thuốc...")
    for m in data.get('medicines', []):
        thuoc = Thuoc(ten_thuoc=m['ten_thuoc'])  # Đã sửa khớp với model
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

    db.session.commit()
    print("--- Hoàn tất import dữ liệu! ---")


if __name__ == '__main__':
    with app.app_context():
        import_json_data()