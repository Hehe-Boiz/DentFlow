function getSchedules(id, day) {
    fetch("/api/get-schedules", {
        method: "post",
        body: JSON.stringify({
            "id": id,
            "day": day,
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        console.log(data)
    });
}

function saveFullProfile() {
    const hoTen = document.getElementById('new_hoten').value;
    const so_dien_thoai = document.getElementById('new_sdt').value;
    const gioiTinh = document.getElementById('new_gioitinh').value;
    const ngaySinh = document.getElementById('new_ngaysinh').value;
    const email = document.getElementById('new_email').value;
    const diaChi = document.getElementById('new_diachi').value;
    const CCCD = document.getElementById('new_CCCD').value;

    // Validate client cơ bản
    if (!hoTen || !so_dien_thoai) {
        alert("Vui lòng nhập Họ tên và Số điện thoại!");
        return;
    }
    const payload = {
        ho_ten: hoTen,
        so_dien_thoai: so_dien_thoai,
        gioi_tinh: gioiTinh,
        ngay_sinh: ngaySinh,
        email: email,
        dia_chi: diaChi
    };
    //Gọi api
    fetch('/api/create-profiles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })

    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            // Đóng modal tạo mới
            const modalEl = document.getElementById('createProfileModal');
            const modalInstance = bootstrap.Modal.getInstance(modalEl);
            modalInstance.hide();
            // Reset form
            document.getElementById('formCreateProfile').reset();
            alert('Tạo thành công')
        } else {
            alert('Lỗi: ' + data.msg);
        }
    })
    .catch(err => console.error(err));
}

