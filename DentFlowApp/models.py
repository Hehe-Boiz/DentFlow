from sqlalchemy import Column, Integer, String, Enum
from DentFlowApp import db,app
from enum import Enum as UserEnum
from flask_login import UserMixin

class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(UserEnum):
    ADMIN = 1
    USER = 2
    RECEPTIONIST = 3
    DOCTOR = 4
    CASHIER = 5


class User(BaseModel, UserMixin):
    name = Column(String(50), nullable=False)
    avatar = Column(String(100))
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    phone = Column(Integer, nullable=False)

    def __str__(self):
        return self.name

class LichHen(BaseModel):
    pass

class BacSi(BaseModel):
    pass


class HoSoKhamBenh(BaseModel):
    pass

class Thuoc(BaseModel):
    pass

class HoaDon(BaseModel):
    pass


# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         import hashlib
#         u = [
#              NguoiDung(name='receptionist', user_role=UserRole.RECEPTIONIST, phone='0123456',
#                   avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg',
#                   username='receptionist', password=str(hashlib.md5("123456".encode('utf-8')).hexdigest())),
#              NguoiDung(name='cashier', user_role=UserRole.CASHIER, phone='01234567',
#                   avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg',
#                   username='cashier', password=str(hashlib.md5("123456".encode('utf-8')).hexdigest())),
#              NguoiDung(name='user', user_role=UserRole.USER, phone='0123456',
#                   avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg',
#                   username='User', password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()))
#              ]
#         for user in u:
#             db.session.add(user)
#         db.session.commit()
