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
    fetch(`/api/profile/${hoSoId}`)
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
            document.getElementById('patientForm').action = `/api/update-profile/${hoSoId}`;
        });
}

let isLoadServices = false
function loadServices(){
    const serviceSelect = document.getElementById('selectService');
    if (!isLoadServices){
        fetch('/api/dich-vu')
        .then(res => res.json())
        .then(data => {
            data.forEach(item => {
                // Tạo thẻ option: <option value="1">Nhổ răng (500k)</option>
                const option = document.createElement('option');
                option.value = item.id;
                // Hiển thị tên kèm giá (format tiền việt)
                const price = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(item.don_gia);
                option.text = `${item.ten_dich_vu} - ${price}`;
                serviceSelect.appendChild(option);
            });
            isLoadServices = true
        })
        .catch(err => console.error("Lỗi load dịch vụ:", err));
    }
}

let isLoadDoctor = false
function loadDoctors() {
    const doctorSelect = document.getElementById('selectDoctor');
    if (!isLoadDoctor){
        fetch('/api/bac-si?trang_thai=san_sang')
            .then(res => res.json())
            .then(data => {
                data.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.ma_bac_si;
                    option.text = `BS.${item.ho_ten}`;
                    option.o
                    doctorSelect.appendChild(option);
                });

                // Đánh dấu là đã load xong -> Lần sau mở modal không cần load lại
                isLoadDoctor = true;
            })
            .catch(err => console.error("Lỗi load bác sĩ:", err));
    }
}

function resetIsLoadServiceAndDoctor(){
    isLoadServices = false
    isLoadDoctor = false
    isLoadTime = false
    console.log(isLoadDoctor)
    console.log(isLoadServices)
}

let isLoadTime = false
function loadAvailableTimes() {
    const timeSelect = document.getElementById('selectTime')
    const doctorSelect = document.getElementById('selectDoctor');
    const daySelect = document.getElementById('selectDay')
    if (!isLoadTime){
        if(doctorSelect.value !== "" && daySelect.value !== ""){
            fetch("/api/lay-thoi-gian-trong", {
                method: "post",
                body: JSON.stringify({
                    "id": doctorSelect.value,
                    "day": daySelect.value,
                }),
                headers: {
                    "Content-Type": "application/json"
                }
            }).then(res => res.json())
              .then(data => {
                data.forEach(item => {
                        const option = document.createElement('option');
                        option.value = item;
                        option.text = `${item}`;
                        timeSelect.appendChild(option);
                    });
            });
            isLoadTime = true
        }
        else {
            alert('Vui lòng nhập đầy đủ ngày và bác sĩ')
        }
    }
}

function initDateInput(){
    const dateInput = document.getElementById('selectDay')
    const today = new Date().toISOString().split('T')[0];
    dateInput.setAttribute('min', today);
}

function resetAvailableTimes(){
    isLoadTime = false
    const timeSelect = document.getElementById('selectTime')
    timeSelect.innerHTML = '<option value="">-- Chọn giờ --</option>'
    console.log(isLoadTime)
}


let searchTimeout = null;
const searchInput = document.getElementById('searchProfileInput');
const resultBox = document.getElementById('searchResultBox');
const hiddenInput = document.getElementById('selectedProfileId');

searchInput.addEventListener('input', function(e) {
    const keyword = e.target.value ? e.target.value.trim() : "";

    if (keyword.length === 0) {
        hiddenInput.value = "";
        resultBox.classList.add('d-none');
        return;
    }

    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    searchTimeout = setTimeout(() => {

        resultBox.classList.remove('d-none');
        resultBox.innerHTML = '<div class="p-3 text-center text-muted"><i class="fas fa-spinner fa-spin"></i> Đang tìm...</div>';

        // Gọi API
        fetch(`/api/profile?kw=${encodeURIComponent(keyword)}&page=1`)
            .then(res => res.json())
            .then(data => {
                renderDropdown(data.data);
            })
            .catch(err => {
                console.error(err);
                resultBox.innerHTML = '<div class="p-3 text-center text-danger">Lỗi kết nối</div>';
            });
    }, 2000);
});

function renderDropdown(profiles) {
    if (!profiles || profiles.length === 0) {
        resultBox.innerHTML = `
            <div class="p-3 text-center text-muted">
                Không tìm thấy khách hàng.<br>
            </div>`;
        return;
    }

    let html = '';
    profiles.forEach(p => {
        // Tạo avatar từ chữ cái đầu tên (VD: Lan -> L)
        const firstLetter = p.ho_ten.charAt(0).toUpperCase();

        // Check năm sinh để hiển thị
        const namSinhStr = p.nam_sinh ? `, ${p.nam_sinh}` : '';

        html += `
        <div class="d-flex align-items-center customer-result-item"
             onclick="selectCustomer('${p.id}', '${p.ho_ten}', '${p.so_dien_thoai}')">

            <div class="avatar-circle">${firstLetter}</div>

            <div class="flex-grow-1">
                <div class="fw-bold text-dark">
                    ${p.ho_ten} <span class="fw-normal text-muted">${namSinhStr}</span>
                </div>
                <div class="meta-text">
                    <i class="fas fa-phone-alt me-1" style="font-size: 10px;"></i> ${p.so_dien_thoai}
                    ${p.dia_chi ? ` • ${p.dia_chi}` : ''}
                </div>
            </div>
        </div>
        `;
    });
    resultBox.innerHTML = html;
}

function selectCustomer(id, name, phone) {
    // Điền thông tin vào ô input
    searchInput.value = name;
    hiddenInput.value = id;

    // Tự điền SĐT xuống ô bên dưới (nếu có)
    const phoneField = document.getElementById('bookingPhone'); // ID ô SĐT trong modal
    if (phoneField) phoneField.value = phone;

    // Ẩn bảng kết quả
    resultBox.classList.add('d-none');
}

document.addEventListener('click', function(e) {
    // Nếu click không trúng ô input và không trúng bảng kết quả
    if (!searchInput.contains(e.target) && !resultBox.contains(e.target)) {
        resultBox.classList.add('d-none');
    }
});

searchInput.addEventListener('focus', function() {
    if (resultBox.innerHTML.trim() !== "") {
        resultBox.classList.remove('d-none');
    }
});
