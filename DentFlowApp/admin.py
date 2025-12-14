from flask import redirect
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose
from DentFlowApp import app,db
from flask_login import current_user,logout_user
from DentFlowApp.models import UserRole, LichHen, BacSi, Thuoc, HoSoBenhNhan

admin = Admin(app=app, name="DentFlow")

class ReceptionistModelView(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST

class AdminModelView(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.vai_tro == UserRole.ADMIN

class CashierModelView(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.vai_tro == UserRole.CASHIER


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self) -> bool:
        return current_user.is_authenticated



admin.add_view(ReceptionistModelView(HoSoBenhNhan, db.session, name="Quản lý hồ sơ"))
admin.add_view(ReceptionistModelView(LichHen, db.session, name="Quản lý Lịch Hẹn"))
admin.add_view(AdminModelView(Thuoc,db.session, name="Quản lý thuốc"))
admin.add_view(LogoutView(name="Đăng xuất"))