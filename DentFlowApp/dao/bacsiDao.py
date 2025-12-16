from DentFlowApp.models import BacSi
from DentFlowApp import db

def get_doctors():
    return BacSi.query.all()

def get_doctors_by_id(id):
    return BacSi.query.get(id)