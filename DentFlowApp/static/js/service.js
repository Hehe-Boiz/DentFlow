function goToURL(btn) {
    const url = btn.dataset.url;
    if (url) {
        window.location.href = url;
    }
}

// RECEPTIONIST
function getDataProfile(so_dien_thoai, ho_ten, user_id) {
    let ht = document.getElementById('input_ho_ten')
    let sdt = document.getElementById('input_so_dien_thoai')
    let u_id = document.getElementById('input_user_id')
    ht.value = ho_ten
    sdt.value = so_dien_thoai
    u_id.value = user_id
    ht.readOnly = true;
    sdt.readOnly = true;
    ht.style.backgroundColor = "#e9ecef";
    sdt.style.backgroundColor = "#e9ecef";
}

//temlate: phieu_dieu_tri_search_service.html
function searchPdt() {
    const maso = document.getElementById('input_maso').value.trim();
    const resultDiv = document.getElementById('result_container');
    const errorDiv = document.getElementById('error_alert_div');
    const loader = document.getElementById('loading_spinner');
    const btn_thanh_toan = document.getElementById('btn-thanh-toan')
    const a_thanh_toan = document.getElementById('a-thanh-toan')
    resultDiv.style.display = 'none';
    errorDiv.style.display = 'none';

    if (!maso) {
        alert("Vui lòng nhập mã phiếu!");
        return;
    }

    loader.style.display = 'block';
    fetch(`/api/phieu-dieu-tri/search?id=${maso}`)
        .then(response => {
            if (!response.ok) throw new Error('Lỗi kết nối hoặc không có quyền');
            return response.json();
        })
        .then(respData => {
            loader.style.display = 'none';
            if (respData.status === 'success' && respData.data.length > 0) {
                const item = respData.data[0];

                let trang_thai = document.getElementById('pdt_trang_thai');
                trang_thai.className = 'badge rounded-pill';
                document.getElementById('pdt_id').innerText = item['id'];
                a_thanh_toan.href = `/cashier/thanh-toan/${item['id']}`
                document.getElementById('pdt_ho_ten').innerText = item['ho_so_benh_nhan.ho_ten'];
                document.getElementById('pdt_dich_vu').innerText = item['dich_vu.ten_dich_vu'];
                const donGia = item['dich_vu.don_gia'];
                document.getElementById('pdt_dongia').innerText = new Intl.NumberFormat('vi-VN', {
                    style: 'currency',
                    currency: 'VND'
                }).format(donGia);
                if (item['trang_thai'] === 'DA_THANH_TOAN') {
                    trang_thai.innerText = 'Đã thanh toán'
                    trang_thai.classList.add('bg-success')
                    btn_thanh_toan.style.display = 'none'

                } else if (item['trang_thai'] === 'CHUA_THANH_TOAN') {
                    trang_thai.innerText = 'Chờ thanh toán'
                    trang_thai.classList.add('bg-warning')
                    btn_thanh_toan.style.display = 'block'
                } else {
                    trang_thai.innerText = 'Hoàn tiền'
                    trang_thai.classList.add('badge bg-primary')
                    btn_thanh_toan.style.display = 'none'

                }
                document.getElementById('pdt_ghichu').innerText = item.ghi_chu || 'Không có';
                resultDiv.style.display = 'block';
            } else {
                errorDiv.innerText = "Không tìm thấy phiếu điều trị này.";
                errorDiv.style.display = 'block';
            }
        })
        .catch(err => {
            loader.style.display = 'none';
            console.error(err);
            errorDiv.innerText = "Lỗi hệ thống, vui lòng thử lại.";
            errorDiv.style.display = 'block';
        });
}


document.addEventListener("DOMContentLoaded", function () {
    // 1. Lấy các phần tử cần thiết
    const inputName = document.getElementById('searchName');
    const inputPhone = document.getElementById('searchPhone');
    const btnSearch = document.getElementById('btnSearch');

    // Kiểm tra nếu các element này thực sự tồn tại (đề phòng lỗi trang khác dùng file này)
    if (!inputName || !inputPhone || !btnSearch) return;

    // 2. Hàm kiểm tra
    function checkInputs() {
        const nameValue = inputName.value.trim();
        const phoneValue = inputPhone.value.trim();

        if (nameValue !== "" || phoneValue !== "") {
            btnSearch.disabled = false;
        } else {
            btnSearch.disabled = true;
        }
    }

    // 3. Lắng nghe sự kiện
    inputName.addEventListener('input', checkInputs);
    inputPhone.addEventListener('input', checkInputs);

    // 4. Chạy kiểm tra ban đầu
    checkInputs();

});
