from flask import jsonify
from DentFlowApp import app
from DentFlowApp.dao import ho_so_benh_nhan_dao


@app.route('/api/patient/<int:id>')
def get_patient_detail(id):
    ho_so = ho_so_benh_nhan_dao.get_ho_so_theo_id(id)
    return jsonify(ho_so.to_dict())