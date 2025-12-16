from DentFlowApp import app,db
from flask import request, redirect, render_template
from flask_login import current_user, login_required
from DentFlowApp import utils

@app.route('/booking')
@login_required
def booking_view():
        return render_template('booking.html', can_do=utils.user_can_do())
