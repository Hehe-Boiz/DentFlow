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

@app.route('/booking-buoc2', methods=['GET','POST'])
def booking_buoc2_view():
        doctors = bacsiDao.get_doctors_is_ready()
        booking_data = session.get('booking_data')
        if not booking_data or 'dich_vu_id' not in booking_data:
                return redirect('/booking')

        if request.method == 'POST':
                # Xử lý khi bấm "Tiếp tục" ở bước 2
                doctor_id = request.form.get('doctor_id')
                booking_date = request.form.get('booking_date')
                time_slot = request.form.get('time_slot')

                # Lưu tiếp thông tin vào session
                session['booking_data']['doctor_id'] = doctor_id
                session['booking_data']['booking_date'] = booking_date
                session['booking_data']['time_slot'] = time_slot

                # Chuyển sang bước 3 (Xác nhận)
                # return redirect(url_for('booking_step3')) # Tạo route này sau
                return "Đã xong bước 2! Dữ liệu trong session: " + str(session['booking_data'])
        return render_template('booking/booking_buoc2.html',doctors=doctors)