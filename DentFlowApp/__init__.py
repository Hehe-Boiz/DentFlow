import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os
app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv('APP_SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
cloudinary.config(cloud_name=os.getenv('CLOUD_NAME'),api_key=os.getenv('CLOUD_API_KEY'),api_secret=os.getenv('CLOUD_API_SECRET'))

login = LoginManager(app=app)
db = SQLAlchemy(app=app)