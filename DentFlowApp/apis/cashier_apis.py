import http

from DentFlowApp import app
from flask import render_template, request
from flask_login import current_user, login_required

from DentFlowApp.dao.bacsi_dao import get_doctors_by_id
from DentFlowApp.dao.thungan_dao import get_phieu_dieu_tri_chua_thanh_toan, get_dich_vu_by_id
from DentFlowApp.models import UserRole


@app.route('/cashier', methods=['GET'])
@login_required
def cashier_view():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.CASHIER:
        page = request.args.get('page', 1, type=int)
        phieu_dieu_tri_s = get_phieu_dieu_tri_chua_thanh_toan(page=page)  # pagination
        return render_template('cashier/cashier.html', thungan=True, pagination=phieu_dieu_tri_s)
    return http.HTTPStatus.FORBIDDEN


@app.route('/cashier/tra-cuu', methods=['GET'])
@login_required
def cashier_phieu_dieu_tri_search():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.CASHIER:
        return render_template('cashier/cashier_search_pdt.html')
    return http.HTTPStatus.FORBIDDEN
