import cloudinary.uploader
from flask import redirect, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose
from flask_admin.model import InlineFormAdmin
from wtforms.fields.simple import PasswordField, FileField

from DentFlowApp import app, db, bcrypt
from flask_login import current_user,logout_user
from DentFlowApp.models import UserRole, LichHen, BacSi, Thuoc, HoSoBenhNhan, NguoiDung, DichVu, ChiTietDichVu

admin = Admin(app=app, name="DentFlow")

class BaseModelView(ModelView):
    page_size = 10

class AdminModelView(BaseModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.vai_tro == UserRole.ADMIN



class UserModelView(AdminModelView):
    column_list = ['id', 'username', 'ho_ten', 'vai_tro', 'is_active']  # Cột hiện trên danh sách
    column_searchable_list = ['username', 'ho_ten']
    column_filters = ['vai_tro']
    create_modal = True
    # Ẩn password hash trên danh sách để bảo mật
    column_exclude_list = ['password', 'avatar']
    form_overrides = {
        'password': PasswordField,
        'avatar': FileField
    }

    # Form nhập liệu: Chỉ hiện những cái cần thiết
    form_columns = ['ho_ten', 'username', 'password', 'vai_tro', 'so_dien_thoai', 'avatar']

    # Hook: Chạy trước khi lưu vào DB -> Để băm mật khẩu
    def on_model_change(self, form, model, is_created):
        raw_pass = form.password.data
        if raw_pass:
            hashed_pass = bcrypt.generate_password_hash(raw_pass).decode('utf-8')
            model.password = hashed_pass
        if form.avatar.data:
            try:
                # Upload lên Cloud
                res = cloudinary.uploader.upload(form.avatar.data)

                # Lấy link ảnh gán vào model
                model.avatar = res.get('secure_url')

            except Exception as e:
                flash(f"Lỗi upload ảnh: {e}")
                # Nếu lỗi thì hủy thao tác gán để không làm hỏng dữ liệu cũ
                del form.avatar


class ChiTietDichVuInLineView(InlineFormAdmin):
    # Chỉ hiện những cột cần nhập
    form_columns = ['id', 'noi_dung_chi_tiet']

    # Tắt việc nhập ID thủ công (vì nó tự lấy ID của cha)
    form_excluded_columns = ['id']

class DichVuModelView(AdminModelView):

    column_list = ['ten_dich_vu', 'don_gia', 'dang_hoat_dong']
    form_columns = ['ten_dich_vu', 'don_gia', 'dang_hoat_dong']

    can_delete = False

    # Cho phép tìm kiếm
    column_searchable_list = ['ten_dich_vu']
    inline_models = (ChiTietDichVuInLineView(ChiTietDichVu),)


class ReceptionistModelView(BaseModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST

class CashierModelView(BaseModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.vai_tro == UserRole.CASHIER

class ManagerModelView(BaseModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.vai_tro == UserRole.MANAGER

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self) -> bool:
        return current_user.is_authenticated


admin.add_view(DichVuModelView(DichVu, db.session, name="Quản lý dịch vụ"))
admin.add_view(UserModelView(NguoiDung, db.session, name="Quản lý người dùng"))
admin.add_view(ReceptionistModelView(HoSoBenhNhan, db.session, name="Quản lý hồ sơ"))
admin.add_view(ReceptionistModelView(LichHen, db.session, name="Quản lý Lịch Hẹn"))
admin.add_view(ManagerModelView(Thuoc, db.session, name="Quản lý thuốc"))
admin.add_view(LogoutView(name="Đăng xuất"))