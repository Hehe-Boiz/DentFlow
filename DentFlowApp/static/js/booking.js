function selectService(element, id, name) {
    // 1. Xóa class 'selected' ở tất cả các item
    const allItems = document.querySelectorAll('.service-item');
    allItems.forEach(item => item.classList.remove('selected'));

    // 2. Thêm class 'selected' vào item vừa bấm
    element.classList.add('selected');

    // 3. Gán giá trị ID vào input ẩn (để gửi về server Flask)
    document.getElementById('selectedServiceId').value = id;
    document.getElementById('selectedServiceName').value = name;

    // 4. Kích hoạt nút Tiếp tục
    document.getElementById('btnContinue').disabled = false;
}


// 1. Xử lý chọn Bác sĩ
function selectDoctor(element, id) {
    // Xóa class selected cũ
    document.querySelectorAll('.doctor-card').forEach(item => item.classList.remove('selected'));
    // Thêm vào card mới chọn
    element.classList.add('selected');
    // Gán ID vào input ẩn
    document.getElementById('selectedDoctorId').value = id;
    // Kiểm tra điều kiện để enable nút tiếp tục
    checkFormValidity();
}

// 2. Xử lý validate form để enable nút "Tiếp tục"
const dateInput = document.getElementById('bookingDate');
const timeInputs = document.querySelectorAll('input[name="time_slot"]');
const doctorInput = document.getElementById('selectedDoctorId');
const btnContinue = document.getElementById('btnContinueStep2');

function checkFormValidity() {
    // Kiểm tra xem đã chọn đủ 3 thứ chưa: Bác sĩ, Ngày, Giờ
    const isDoctorSelected = doctorInput.value !== "";
    const isDateSelected = dateInput.value !== "";
    let isTimeSelected = false;
    timeInputs.forEach(input => {
        if (input.checked) isTimeSelected = true;
    });

    // Nếu đủ cả 3 thì enable nút
    if (isDoctorSelected && isDateSelected && isTimeSelected) {
        btnContinue.disabled = false;
    } else {
        btnContinue.disabled = true;
    }
}

// Lắng nghe sự kiện thay đổi của Ngày và Giờ
dateInput.addEventListener('change', checkFormValidity);
timeInputs.forEach(input => {
    input.addEventListener('change', checkFormValidity);
});

// Thiết lập ngày tối thiểu là hôm nay
const today = new Date().toISOString().split('T')[0];
dateInput.setAttribute('min', today);