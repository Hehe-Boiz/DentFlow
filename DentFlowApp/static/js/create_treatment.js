const buttons = document.querySelectorAll('.tab-btn');
const tabs = document.querySelectorAll('.tab-content');

buttons.forEach(btn => {
    btn.addEventListener('click', () => {
        const target = btn.dataset.tab;

        // Ẩn tất cả tab
        tabs.forEach(tab => tab.classList.add('hidden'));

        // Hiện tab được chọn
        document.getElementById(target).classList.remove('hidden');
    });
});

const btn = document.getElementById("btn-ke-don");
const container = document.getElementById("ke-don-container");
let loaded = false;

btn.addEventListener("click", async () => {
    // Nếu đã load rồi thì toggle ẩn/hiện
    if (loaded) {
        container.classList.toggle("hidden");
        return;
    }

    // Gọi server lấy HTML
    const res = await fetch("/treatments/ke-don");
    const html = await res.text();

    // Nhét HTML vào sau button
    container.innerHTML = html;
    loaded = true;

    initTimeButtons();
    checkLoThuoc();
});

const serviceSelect = document.getElementById('service-select');
const priceInput = document.getElementById('service-price');

if (serviceSelect && priceInput) {
    serviceSelect.addEventListener('change', function () {
        // Lấy option đang được chọn
        const selectedOption = this.options[this.selectedIndex];

        // Lấy giá trị từ thuộc tính data-price
        const price = selectedOption.getAttribute('data-price');

        // Cập nhật vào ô nhập liệu Chi phí
        priceInput.value = price || 0;
    });
}

// thêm dịch vụ
const btnAdd = document.getElementById('btn-add-service');
const tableBody = document.getElementById('service-table-body');
const totalDisplay = document.getElementById('total-amount');
const listContainer = document.getElementById('service-list-container');

let totalAmount = 0;
let stt = 0;

// Hàm format tiền tệ (Ví dụ: 350000 -> 350.000 đ)
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN').format(amount) + ' đ';
};

if (btnAdd) {
    btnAdd.addEventListener('click', function () {
        const serviceSelect = document.getElementById('service-select');
        const priceInput = document.getElementById('service-price');
        const noteInput = document.getElementById('service-note');

        const serviceId = serviceSelect.value;
        const serviceName = serviceSelect.options[serviceSelect.selectedIndex].text;
        const price = parseFloat(priceInput.value) || 0;
        const note = noteInput.value || '-';

        if (!serviceId) {
            alert("Vui lòng chọn một dịch vụ!");
            return;
        }

        if (listContainer.classList.contains('hidden')) {
            listContainer.classList.remove('hidden');
        }

        // 1. Tăng STT và cập nhật tổng tiền
        stt++;
        totalAmount += price;

        // 2. Tạo hàng mới
        const row = document.createElement('tr');
        row.className = "hover:bg-gray-50 transition-colors";
        row.innerHTML = `
                <td class="py-3 px-4 text-sm">${stt}</td>
                <td class="py-3 px-4 text-sm text-gray-900">${serviceName}</td>
                <td class="py-3 px-4 text-sm text-emerald-700 font-medium">${formatCurrency(price)}</td>
                <td class="py-3 px-4 text-sm text-gray-600">${note}</td>
                <td class="py-3 px-4">
                    <button type="button" class="btn-delete text-red-600 hover:text-red-800 p-2 rounded" data-price="${price}">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                    </button>
                </td>
            `;

        tableBody.appendChild(row);

        // 3. Cập nhật hiển thị tổng tiền
        totalDisplay.innerText = formatCurrency(totalAmount);

        // 4. Xử lý sự kiện xóa hàng
        row.querySelector('.btn-delete').addEventListener('click', function () {
            const priceToRemove = parseFloat(this.getAttribute('data-price'));
            totalAmount -= priceToRemove;

            // 2. Cập nhật hiển thị tổng tiền
            totalDisplay.innerText = formatCurrency(totalAmount);

            // 3. Xóa hàng khỏi giao diện
            row.remove();

            // 4. Đánh lại số thứ tự (STT) cho các hàng còn lại
            const rows = tableBody.querySelectorAll('tr');
            stt = rows.length; // Cập nhật lại biến đếm stt toàn cục
            rows.forEach((r, index) => {
                r.querySelector('td:first-child').innerText = index + 1;
            });

            // 5. Kiểm tra ẩn bảng nếu hết dịch vụ
            if (rows.length === 0) {
                listContainer.classList.add('hidden');
                stt = 0;
                totalAmount = 0; // Đảm bảo tổng về 0
            }
        });

        // 5. Reset ô nhập sau khi thêm
        serviceSelect.value = "";
        priceInput.value = 0;
        noteInput.value = "";

    });
}

function initTimeButtons() {
    const buttons_time = document.querySelectorAll('.time-btn');
    buttons_time.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons_time.forEach(b => {
                b.classList.remove('bg-blue-600', 'text-white');
                b.classList.add('bg-gray-200', 'text-gray-700');
            });
            btn.classList.remove('bg-gray-200', 'text-gray-700');
            btn.classList.add('bg-blue-600', 'text-white');
        });
    });
}

function checkLoThuoc() {
    const selectThuoc = document.getElementById('select-ten-thuoc');
    const inputSoNgay = document.getElementById('input-so-ngay');
    const inputHanSuDung = document.getElementById('input-han-su-dung');
    const warningBox = document.getElementById('warning-box');
    const warningText = document.getElementById('warning-text');
    const inputDonVi = document.getElementById('input-don-vi');

    let debounceTimer;

    function fetchLoThuocPhuHop() {
        const thuocId = selectThuoc.value;
        const soNgay = inputSoNgay.value;

        // Reset UI states
        warningBox.classList.add('hidden');
        inputHanSuDung.value = '';
        inputHanSuDung.classList.remove('text-red-600', 'font-bold');

        if (!thuocId || !soNgay || soNgay <= 0 ||) {
            return;
        }

        inputHanSuDung.value = "Đang tìm kiếm...";

        fetch(`/api/thuoc/${thuocId}/lo-phu-hop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({so_ngay_dung: soNgay})
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Tìm thấy lô phù hợp
                    const lo = data.data;
                    inputHanSuDung.value = `${lo.han_su_dung} (Lô: ${lo.so_lo})`;
                    inputHanSuDung.classList.remove('text-red-600');
                    inputHanSuDung.classList.add('text-green-700');
                } else {
                    // Không tìm thấy hoặc có cảnh báo (hết hạn, ko đủ ngày)
                    inputHanSuDung.value = "Không khả dụng";
                    inputHanSuDung.classList.add('text-red-600', 'font-bold');

                    // Hiển thị warning box với nội dung từ server
                    warningText.innerText = data.message || "Không tìm thấy lô thuốc phù hợp.";
                    warningBox.classList.remove('hidden');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                inputHanSuDung.value = "Lỗi kiểm tra";
            });
    }

    // Hàm debounce để delay gọi API
    function handleInput() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(fetchLoThuocPhuHop, 500); // Đợi 500ms sau khi ngừng nhập
    }

    // Gán sự kiện
    selectThuoc.addEventListener('change', fetchLoThuocPhuHop); // Gọi ngay khi đổi thuốc
    inputSoNgay.addEventListener('input', handleInput);       // Gọi debounce khi nhập số ngày

}