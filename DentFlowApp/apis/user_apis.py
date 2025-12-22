from flask import render_template
from flask_login import login_required, current_user

from DentFlowApp import app

@app.route("/user")
@login_required
def user_view():
    ho_so = current_user.ho_so_benh_nhan
    return render_template("user/user.html", ho_so=ho_so)