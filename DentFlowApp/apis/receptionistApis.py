import http

from DentFlowApp import app, db
from flask import request, redirect, render_template
from flask_login import current_user, login_required
from DentFlowApp import utils
from DentFlowApp.dao import receptionistDao
from DentFlowApp.models import UserRole


@app.route('/receptionist/search_pdt_view', methods=['GET'])
@login_required
def search_pdt_view():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
        can_do = utils.user_can_do()
        receiver_code = request.args.get('code')
        phieu_dieu_tri = None
        if receiver_code:
            phieu_dieu_tri = receptionistDao.get_phieu_dieu_tri_by_maso(receiver_code)

        return render_template('phieu_dieu_tri_search_service.html', can_do=can_do, phieu_dieu_tri=phieu_dieu_tri)
    return http.HTTPStatus.NOT_FOUND


@app.route('/receptionist/register_profile_user', methods=['GET'])
@login_required
def create_profile_user_view():
    if current_user.is_authenticated and current_user.vai_tro == UserRole.RECEPTIONIST:
        can_do = utils.user_can_do()
        return render_template('user_registration_service.html', can_do=can_do)
    return http.HTTPStatus.NOT_FOUND


@app.route('/receptionist', methods=['POST'])
@login_required
def payment_post():
    pass
