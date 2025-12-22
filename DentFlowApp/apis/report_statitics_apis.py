# FOR ROLE MANAGER
import http
import os

from wtforms.validators import any_of

from DentFlowApp import app, db
from flask import render_template, request, jsonify
from flask_login import current_user, login_required
from DentFlowApp.dao.receptionistDao import get_phieu_dieu_tri_by_id
from DentFlowApp.dao.thungan_dao import get_phieu_dieu_tri_chua_thanh_toan, \
    get_ds_phieu_dieu_tri_da_thanh_toan
from DentFlowApp.models import UserRole, TrangThaiThanhToan, HoaDon, PhuongThucThanhToan


@app.route('/manager', methods=['GET'])
@login_required
def manager_view():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.MANAGER:
        return render_template('manager/manager.html', quanly=True)
    return http.HTTPStatus.FORBIDDEN
