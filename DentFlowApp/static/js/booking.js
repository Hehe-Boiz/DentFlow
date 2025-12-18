const dateInput = document.getElementById('bookingDate');
const doctorInput = document.getElementById('selectedDoctorId');
const btnContinue = document.getElementById('btnContinueStep2');



function selectService(element, id, name) {

    const allItems = document.querySelectorAll('.service-item');
    allItems.forEach(item => item.classList.remove('selected'));

    element.classList.add('selected');

    document.getElementById('selectedServiceId').value = id;
    document.getElementById('selectedServiceName').value = name;

    document.getElementById('btnContinue').disabled = false;
}

function selectDoctor(element, id, name) {

    document.querySelectorAll('.doctor-card').forEach(item => item.classList.remove('selected'));

    element.classList.add('selected');

    document.getElementById('selectedDoctorId').value = id;
    document.getElementById('selectedDoctorName').value = name;

    if(dateInput.value !== ""){
        getAvailableTimeSlots(doctorInput.value, dateInput.value)
    }
}

function getAvailableTimeSlots(id, day) {
    fetch("/api/get-available-time-slots", {
        method: "post",
        body: JSON.stringify({
            "id": id,
            "day": day,
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        renderSlots(data)
    });
}

function layDanhSach(){
    if (doctorInput.value !== "" && dateInput.value !== ""){
        console.log(doctorInput.value)
        getAvailableTimeSlots(doctorInput.value, dateInput.value)
    }else{
        console.log('nothing happen')
    }
}

dateInput.addEventListener('change', function(){
    layDanhSach();
});

function renderSlots(slots) {
    const slotContainer = document.getElementById('timeSlotContainer');
    const waitingMsg = document.getElementById('slotWaitingMessage');
    const noSlotMsg = document.getElementById('noSlotMessage');

    // Xóa nội dung cũ
    slotContainer.innerHTML = '';

    if (slots.length === 0) {
        // Trường hợp kín lịch
        waitingMsg.classList.add('d-none');
        slotContainer.classList.add('d-none');
        noSlotMsg.classList.remove('d-none');
    } else {
        // Trường hợp có lịch -> Hiển thị Container
        waitingMsg.classList.add('d-none');
        noSlotMsg.classList.add('d-none');
        slotContainer.classList.remove('d-none');

        // Vòng lặp tạo nút
        slots.forEach((slot, index) => {
            // 1. Tạo thẻ cột (col) bao bên ngoài
            const colDiv = document.createElement('div');
            colDiv.className = 'col';

            // 2. Tạo nội dung bên trong (Input ẩn + Label nút bấm)
            // Lưu ý: btn-outline-primary giúp nút có viền xanh, khi chọn sẽ tô màu xanh
            colDiv.innerHTML = `
                <input type="radio" class="btn-check text-center" name="time_slot" id="slot_${index}" value="${slot}" autocomplete="off">
                <label class="btn btn-outline-primary w-100 fw-medium py-2" for="slot_${index}">
                    ${slot}
                </label>
            `;

            // 3. Thêm vào container
            slotContainer.appendChild(colDiv);
        });
    }
}

function checkFormValidity() {
    let isDoctorSelected = doctorInput.value !== "";
    let isDateSelected = dateInput.value !== "";
    let timeInputs = document.querySelectorAll('input[name="time_slot"]');
    let errorMsg = document.getElementById('formErrorMessage');
    let form = document.getElementById('bookingFormStep2');
    let isTimeSelected = false;
    timeInputs.forEach(input => {
        if (input.checked)
            isTimeSelected = true;
    });
    console.log(isTimeSelected, isDoctorSelected, isDateSelected)
    if (isTimeSelected && isDoctorSelected && isDateSelected){
        errorMsg.classList.add('d-none');
        form.submit()
    } else {
        errorMsg.classList.remove('d-none');
        console.log("Thiếu thông tin:", {
            BacSi: isDoctorSelected,
            Ngay: isDateSelected,
            Gio: isTimeSelected
        });
    }
}


// Thiết lập ngày tối thiểu là hôm nay
const today = new Date().toISOString().split('T')[0];
dateInput.setAttribute('min', today);