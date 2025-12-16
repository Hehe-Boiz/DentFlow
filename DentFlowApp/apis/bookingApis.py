from DentFlowApp import app,db
from flask import request, redirect, render_template, session
from flask_login import current_user, login_required
from DentFlowApp import utils
from DentFlowApp.dao import dichvuDao, bacsiDao


@app.route('/booking')
@login_required
def booking_view():
        services = dichvuDao.get_services()
        return render_template('booking/booking.html', services=services)

@app.route('/booking/chon-dich-vu', methods=['post'])
def chon_dich_vu():
        dich_vu_id = request.form.get('service_id')
        ten_dich_vu = request.form.get('service_name')
        if dich_vu_id:
                booking_data = {
                        'dich_vu_id': dich_vu_id,
                        'ten_dich_vu': ten_dich_vu
                }
                session['booking_data'] = booking_data
                return redirect('/booking-buoc2')

@app.route('/booking-buoc2')
def booking_buoc2_view():
        doctors = bacsiDao.get_doctors()
        return render_template('booking/booking_buoc2.html',doctors=doctors)