from DentFlowApp.models import DichVu
from DentFlowApp import db

def get_services():
    return DichVu.query.all()

def get_services_by_id(id):
    return DichVu.query.get(id)

