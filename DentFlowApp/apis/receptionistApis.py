from DentFlowApp import app,db
from flask import request, redirect, render_template
from flask_login import current_user, login_required
from DentFlowApp import utils
from DentFlowApp.dao import receptionistDao


@app.route('/receptionist', methods=['GET'])
@login_required
def payment_view():
    receiver_code = request.args.get('code')
    phieu_dieu_tri = None
    if receiver_code:
        phieu_dieu_tri = paymentDao.get_phieu_dieu_tri_by_maso(receiver_code)

    return render_template('receptionist.html', can_do=utils.user_can_do(), phieu_dieu_tri=phieu_dieu_tri)

@app.route('/receptionist', methods=['POST'])
@login_required
def payment_post():
    pass