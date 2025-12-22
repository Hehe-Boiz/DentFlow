from functools import wraps
from flask import abort, redirect, url_for, request
from flask_login import current_user
from DentFlowApp.models import UserRole

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login_view',next=request.url))
            if current_user.vai_tro not in allowed_roles:
            # Trả về lỗi 403 không được phép truy cập
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required([UserRole.ADMIN])(f)

def receptionist_required(f):
    return role_required([UserRole.RECEPTIONIST])(f)

def doctor_required(f):
    return role_required([UserRole.DOCTOR])(f)
