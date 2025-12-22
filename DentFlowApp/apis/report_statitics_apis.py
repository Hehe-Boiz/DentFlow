# FOR ROLE MANAGER

from DentFlowApp import app
from flask import render_template

from DentFlowApp.dao.hoadon_dao import get_all_hoa_don
from DentFlowApp.decorators import manager_required


@app.route('/manager', methods=['GET'])
@manager_required
def manager_view():
    ds_hoadon = get_all_hoa_don()
    return render_template('manager/manager.html', quanly=True, ds_hoadon=ds_hoadon)
