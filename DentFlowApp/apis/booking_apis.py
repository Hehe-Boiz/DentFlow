from DentFlowApp import app,db
from flask import request, redirect, render_template, session, flash
from flask_login import current_user, login_required
from DentFlowApp import utils
from DentFlowApp.dao import dichvu_dao, bacsi_dao, lich_hen_dao,ho_so_benh_nhan_dao


@app.route('/booking')
@login_required
def booking_view():
        services = dichvu_dao.get_dich_vu()
        return render_template('booking/booking.html', services=services)

@app.route('/booking/choose-service', methods=['post'])
@login_required
def chon_dich_vu():
        dich_vu_id = request.form.get('service_id')
        ten_dich_vu = request.form.get('service_name')
        if dich_vu_id:
                booking_data = {
                        'service_id': dich_vu_id,
                        'service_name': ten_dich_vu
                }
                session['booking_data'] = booking_data
                return redirect('/booking/choose-time-and-doctor')

@app.route('/booking/choose-time-and-doctor', methods=['GET','POST'])
@login_required
def booking_2_view():
        doctors = bacsi_dao.get_doctors_is_ready()
        booking_data = session.get('booking_data')
        if not booking_data or 'service_id' not in booking_data:
                return redirect('/booking')

        if request.method == 'POST':
                # Xử lý khi bấm "Tiếp tục" ở bước 2
                doctor_id = request.form.get('doctor_id')
                booking_date = request.form.get('booking_date')
                time_slot = request.form.get('time_slot')
                doctor_name = request.form.get('doctor_name')
                # Lưu tiếp thông tin vào session
                booking_data['doctor_name'] = doctor_name
                booking_data['doctor_id'] = doctor_id
                booking_data['booking_date'] = booking_date
                booking_data['time_slot'] = time_slot
                session['booking_data'] = booking_data
                # Chuyển sang bước 3 (Xác nhận)
                # return redirect(url_for('booking_step3')) # Tạo route này sau
                return redirect('/booking/confirm_booking')
        return render_template('booking/booking_2.html',doctors=doctors)


@app.route('/booking/confirm_booking', methods=['GET', 'POST'])
@login_required
def booking_3_view():
        booking_data = session.get('booking_data')
        print(booking_data)
        print(booking_data['service_id'])
        print(booking_data['doctor_id'])
        # Nếu chưa có dữ liệu (chưa qua bước 1, 2) thì đá về trang đầu
        if not booking_data or 'service_id' not in booking_data or 'doctor_id' not in booking_data:
                return redirect('/booking/choose-time-and-doctor')

        # 2. Truy vấn DB để lấy thông tin chi tiết hiển thị ra màn hình
        ten_dich_vu = booking_data['service_name']
        dich_vu_id = booking_data['service_id']
        ten_bac_si = booking_data['doctor_name']
        bac_si_id = booking_data['doctor_id']


        # Format lại ngày giờ cho đẹp
        ngay_dat = booking_data['booking_date']  # YYYY-MM-DD
        gio_kham = booking_data['time_slot']
        # --- XỬ LÝ KHI BẤM NÚT "XÁC NHẬN ĐẶT LỊCH" (POST) ---
        if request.method == 'POST':
                ghi_chu = request.form.get('note')
                print(ghi_chu)
                try:
                        ho_so_id = None
                        if current_user.ho_so_benh_nhan is None:
                                ho_so_nguoi_dung = ho_so_benh_nhan_dao.add_ho_so(
                                        ho_ten=current_user.ho_ten,
                                        so_dien_thoai=current_user.so_dien_thoai
                                )
                                ho_so_id = ho_so_nguoi_dung.id
                                print('Add Oke')
                        else:
                                ho_so_id = current_user.ho_so_nguoi_dung.id
                        lich_hen_dao.add_lich_hen(
                                ho_so_benh_nhan_id=ho_so_id,
                                ngay_dat=ngay_dat,
                                gio_kham=gio_kham,
                                bac_si_id=bac_si_id,
                                dich_vu_id=dich_vu_id,
                                ghi_chu=ghi_chu
                        )
                        del session['booking_data']
                        flash('Đặt lịch thành công!' 'booking_completed')
                        return redirect('/')

                except Exception as e:
                        print(e)
                        flash('Lỗi: ' + str(e), 'danger')

        # --- GET REQUEST: Render giao diện ---
        return render_template('booking/booking_3.html',
                               ten_dich_vu=ten_dich_vu,
                               ten_bac_si=ten_bac_si,
                               ngay_dat=ngay_dat,
                               gio_kham=gio_kham)


# Route trang thành công (Đơn giản)
@app.route('/booking/success')
def booking_success():
        return render_template('booking/booking_success.html')