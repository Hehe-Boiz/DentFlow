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

    fetch('/api/create-profiles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })

    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {

            const modalEl = document.getElementById('createProfileModal');
            const modalInstance = bootstrap.Modal.getInstance(modalEl);
            modalInstance.hide();

            document.getElementById('formCreateProfile').reset();
            alert('Tạo thành công')
        } else {
            alert('Lỗi: ' + data.msg);
        }
    })
    .catch(err => console.error(err));
}

const alerts = document.querySelectorAll('[role="alert"]');
alerts.forEach(function(alert) {

    setTimeout(function() {

        let bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
});



const toggleBtn = document.querySelectorAll('.btn-toggle-password');
toggleBtn.forEach(button => {
    button.addEventListener('click', function () {
            let passwordInput = document.querySelector(this.getAttribute('data-target'));
            let icon = this.querySelector('i');
            let type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            if (type === 'text') {
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
})
