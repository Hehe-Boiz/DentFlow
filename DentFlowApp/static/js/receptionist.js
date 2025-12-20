function confirmBookedAppointment(lichHenId) {
    // 1. Xác nhận nhẹ (Optional)
    if (confirm("Bạn có chắc chắn muốn xác nhận lịch hẹn này?") === true){
        let actionDiv = document.getElementById(`action-area-${lichHenId}`);
        console.log(actionDiv)
         // Hiệu ứng loading tạm thời (cho người dùng biết đang chạy)
        const originalContent = actionDiv.innerHTML;
        actionDiv.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"></div> Đang xử lý...';
        // 3. Gọi API Backend
        fetch(`/receptionist/appointment/${lichHenId}?tab=schedule`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Ghi đè HTML cũ bằng HTML mới
                actionDiv.innerHTML = `
                    <span class="badge badge-soft-success px-3 py-2 fw-normal" >
                    Đã xác nhận
                    </span>
                    <a href="#"
                       class="btn btn-outline-primary btn-md px-3 fw-medium rounded-pill d-flex align-items-center text-nowrap">
                        <i class="fas fa-print me-2"></i> Xuất phiếu
                    </a>
                `;

                // Thêm chút hiệu ứng CSS cho mượt (Optional)
                // actionDiv.style.opacity = 0;
                // setTimeout(() => actionDiv.style.opacity = 1, 100);

            } else {
                // Thất bại -> Trả lại nút cũ và báo lỗi
                actionDiv.innerHTML = originalContent;
                alert('Lỗi: ' + data.msg);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            actionDiv.innerHTML = originalContent;
            alert('Có lỗi xảy ra khi kết nối server.');
        });
    }
}

function deleteBookedAppointment(lichHenId) {
    // 1. Xác nhận nhẹ (Optional)
    if (confirm("Bạn có chắc chắn muốn hủy lịch hẹn này?") === true){
        let actionDiv = document.getElementById(`action-delete-${lichHenId}`);
        console.log(actionDiv)
        actionDiv.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"></div> Đang xóa...';
        // 3. Gọi API Backend
        fetch(`/receptionist/appointment/${lichHenId}?tab=schedule`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log(data.status)
                // Xóa đối tượng khỏi giao diện
                actionDiv.remove()
            } else {
                // Thất bại -> Trả lại nút cũ và báo lỗi
                alert('Lỗi: ' + data.msg);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Có lỗi xảy ra khi kết nối server.');
        });
    }
}

function disableEditMode() {
    // Khóa lại tất cả input
    const inputs = document.querySelectorAll('#patientModal input, #patientModal select, #patientModal textarea');
    inputs.forEach(input => input.disabled = true);

    // Hiện nút Sửa, ẩn nút Lưu
    document.getElementById('btnEnableEdit').classList.remove('d-none');
    document.getElementById('btnSave').classList.add('d-none');
}

function enableEditMode() {
    // Bỏ thuộc tính disabled của tất cả input
    const inputs = document.querySelectorAll('#patientModal input, #patientModal select, #patientModal textarea');
    inputs.forEach(input => input.disabled = false);

    // Ẩn nút Sửa, hiện nút Lưu
    document.getElementById('btnEnableEdit').classList.add('d-none');
    document.getElementById('btnSave').classList.remove('d-none');
}

function fillModalData(hoSoId) {
    disableEditMode();
    // Hiện loading trong lúc chờ (Optional)
    // document.getElementById('modal_ho_ten').value = "Đang tải...";

    // Gọi về Server lấy dữ liệu mới nhất
    fetch(`/api/patient/${hoSoId}`)
        .then(res => res.json())
        .then(hs => {
            console.log(hs)
            // Điền dữ liệu y hệt Cách 1
            document.getElementById('modal_id').value = hs.id;
            document.getElementById('modal_ho_ten').value = hs.ho_ten;
            document.getElementById('modal_sdt').value = hs.so_dien_thoai;
            document.getElementById('modal_email').value = hs.email;
            document.getElementById('modal_ngay_sinh').value = hs.ngay_sinh;
            document.getElementById('modal_cccd').value = hs.cccd;
            document.getElementById('modal_dia_chi').value = hs.dia_chi;
            document.getElementById('modal_gioi_tinh').value = hs.gioi_tinh;

            // Cập nhật action
            document.getElementById('patientForm').action = `/receptionist/update-profiles/${hoSoId}`;
        });
}