import hashlib
import cloudinary.uploader
from DentFlowApp.models import NguoiDung
from DentFlowApp import db



def get_user_by_id(id):
    return NguoiDung.query.get(id)

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return NguoiDung.query.filter(NguoiDung.username==username.strip(),
                             NguoiDung.password==password).first()


def add_user(name,phone, username, password, avatar):
    u = NguoiDung(name=name,
             phone=phone,
             username=username.strip(),
             password=str(hashlib.md5(password.strip().encode('utf-8')).hexdigest()))

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()