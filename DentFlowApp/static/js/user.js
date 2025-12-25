const fileInput = document.getElementById('uploadAvatarInput');
const fileNameDisplay = document.getElementById('fileNameDisplay');

fileInput.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {

        fileNameDisplay.textContent = 'Đã chọn: ' + file.name;


        fileNameDisplay.classList.remove('text-muted', 'fst-italic');
        fileNameDisplay.classList.add('text-primary', 'fw-bold');
    } else {

        fileNameDisplay.textContent = 'JPG, PNG tối đa 2MB.';
        fileNameDisplay.classList.add('text-muted', 'fst-italic');
        fileNameDisplay.classList.remove('text-primary', 'fw-bold');
    }
});

function deleteAppointment(){
    if(confirm("Bạn có chắc chắn muốn xóa lịch hẹn này?") === true){
        let form = document.getElementById('delAppointment')
        form.submit()
    }
}