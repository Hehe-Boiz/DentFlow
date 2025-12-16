function selectService(element, id, name) {

    const allItems = document.querySelectorAll('.service-item');
    allItems.forEach(item => item.classList.remove('selected'));

    element.classList.add('selected');

    document.getElementById('selectedServiceId').value = id;
    document.getElementById('selectedServiceName').value = name;

    document.getElementById('btnContinue').disabled = false;
}



function selectDoctor(element, id) {

    document.querySelectorAll('.doctor-card').forEach(item => item.classList.remove('selected'));

    element.classList.add('selected');

    document.getElementById('selectedDoctorId').value = id;

    if(dateInput.value !== ""){
        getSchedules(doctorInput.value, dateInput.value)
    }
    checkFormValidity();
}

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


function lay_danh_sach(){
    if (doctorInput.value !== "" && dateInput.value !== ""){
        console.log(doctorInput.value)
        getSchedules(doctorInput.value, dateInput.value)
    }else{
        console.log('nothing happen')
    }
}

dateInput.addEventListener('change', lay_danh_sach);

//timeInputs.forEach(input => {
//    input.addEventListener('change', checkFormValidity);
//});

// Thiết lập ngày tối thiểu là hôm nay
const today = new Date().toISOString().split('T')[0];
dateInput.setAttribute('min', today);