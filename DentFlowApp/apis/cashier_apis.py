import http
from DentFlowApp import app
from flask import render_template
from flask_login import current_user, login_required
from DentFlowApp.models import UserRole


@app.route('/cashier', methods=['GET'])
@login_required
def cashier_view():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.CASHIER:
        return render_template('cashier/cashier.html')
    return http.HTTPStatus.FORBIDDEN


@app.route('/cashier/tra-cuu', methods=['GET'])
@login_required
def cashier_phieu_dieu_tri_search():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.CASHIER:
        return render_template('cashier/cashier_search_pdt.html')
    return http.HTTPStatus.FORBIDDEN
