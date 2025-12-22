from flask import render_template, request, flash, redirect
from flask_login import login_required, current_user
from pyexpat.errors import messages

from DentFlowApp.dao import lich_hen_dao, user_dao
from DentFlowApp import app
from DentFlowApp import utils

@app.route("/user")
@login_required
def user_view():
    ho_so = current_user.ho_so_benh_nhan
    lich_hen = None
    if ho_so is not None:
        lich_hen = lich_hen_dao.get_lich_hen(ho_so_benh_nhan_id=ho_so.id)
    print(lich_hen)
    return render_template("user/user.html", ho_so=ho_so, lich_hen=lich_hen)

@app.route("/user/update-user/<int:user_id>", methods=['POST'])
@login_required
def update_user(user_id):
    try:
        ho_ten = request.form.get('ho_ten')
        print(ho_ten)
        so_dien_thoai = request.form.get('so_dien_thoai')
        print(so_dien_thoai)
        is_valid, error_msg = utils.validate_thong_tin_benh_nhan(ho_ten=ho_ten, sdt=so_dien_thoai)
        if not is_valid:
            flash(error_msg, 'update_failed')
            return redirect('/user')
        avatar = request.files.get('avatar')
        print(avatar)
        user_dao.update_user(id=user_id
                             ,ho_ten=ho_ten
                             ,so_dien_thoai=so_dien_thoai
                             ,avatar=avatar)
        flash('Cập nhật thành công', 'success')
    except Exception as ex:
        flash(str(ex), 'failed')
    return redirect('/user')


