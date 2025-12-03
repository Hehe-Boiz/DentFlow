import hashlib
import cloudinary.uploader
from DentFlowApp.models import User
from DentFlowApp import db



def get_user_by_id(id):
    return User.query.get(id)

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username==username.strip(),
                             User.password==password).first()


def add_user(name,phone, username, password, avatar):
    u = User(name=name,
             phone=phone,
             username=username.strip(),
             password=str(hashlib.md5(password.strip().encode('utf-8')).hexdigest()))

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()