import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)

app.secret_key = '123456'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/dentalflowdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
cloudinary.config(cloud_name='dkvrjdbl6',api_key='277952256147366',api_secret='SR4ggGob7vTjSFp-7Yg11mqjFiE')

login = LoginManager(app=app)
login.login_view = 'login_view'
db = SQLAlchemy(app=app)

from DentFlowApp.apis import loginApis, bookingApis


