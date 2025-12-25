import hashlib
import cloudinary.uploader
from DentFlowApp.models import NguoiDung
from DentFlowApp import db, bcrypt


def get_user_by_id(id):
    return NguoiDung.query.get(id)

def auth_user(username, password):
    user = NguoiDung.query.filter(NguoiDung.username==username.strip()).first()
    if user and bcrypt.check_password_hash(user.password, password.strip()):
        return user
    return None


def add_user(ho_ten, so_dien_thoai, username, password, avatar):
    u = NguoiDung(ho_ten=ho_ten,
             so_dien_thoai=so_dien_thoai,
             username=username.strip().lower(),
             password=bcrypt.generate_password_hash(password.strip()).decode('utf-8'))

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()

def update_user(user=None, id=None, **kwargs):
    u = user
    if u is None and id is not None:
        u = get_user_by_id(id)
    if not u:
        raise Exception('Không có user')
    for key, value in kwargs.items():
        if value:
            if key == 'password':
                u.password = value
                print(value)
            if key == 'ho_ten':
                u.ho_ten = value
                print(value)
            if key == 'so_dien_thoai':
                u.so_dien_thoai = value
                print(value)
            if key == 'password':
                u.password = value
                print(value)
            elif key == 'avatar':
                res = cloudinary.uploader.upload(value)
                u.avatar = res.get('secure_url')
                print(u.avatar)
    try:
        db.session.commit()
    except Exception as ex:
        db.session.rollback()
        raise Exception('Cập nhật thất bại')