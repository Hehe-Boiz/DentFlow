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
    inputUnit();
    initAddMedicineEvent();
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

function inputUnit() {
    const thuocSelect = document.getElementById('select-ten-thuoc');
    const unitInput = document.getElementById('input-don-vi');

    if (thuocSelect && unitInput) {
        thuocSelect.addEventListener('change', function () {
            // Lấy option đang được chọn
            const selectedOption = this.options[this.selectedIndex];
            // Lấy giá trị từ thuộc tính data-unit
            const unit = selectedOption.getAttribute('data-unit');
            console.log(unit);

            // Cập nhật vào ô nhập liệu Chi phí
            unitInput.value = unit || "viên";
        });
    }
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

        // if (!thuocId || !soNgay || soNgay <= 0) {
        //     return;
        // }

        if (soNgay <= 0) {
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

let danhSachThuocKeDon = [];

// Hàm khởi tạo sự kiện cho nút Thêm Thuốc
function initAddMedicineEvent() {
    const btnThemThuoc = document.getElementById('id-add-thuoc'); // Nút thêm thuốc

    if (btnThemThuoc) {
        // Xóa event cũ để tránh bị double click nếu gọi hàm nhiều lần
        const newBtn = btnThemThuoc.cloneNode(true);
        btnThemThuoc.parentNode.replaceChild(newBtn, btnThemThuoc);

        newBtn.addEventListener('click', function () {
            handleAddMedicine();
        });
    }
}

function handleAddMedicine() {
    // 1. Lấy các Element
    const selectThuoc = document.getElementById('select-ten-thuoc');
    const inputLieuDung = document.querySelector('input[type="number"][placeholder="2"]'); // Input Liều dùng
    const inputDonVi = document.getElementById('input-don-vi');
    const inputSoNgay = document.getElementById('input-so-ngay');
    const selectThoiDiem = document.getElementById('select-thoi-diem');

    // Lấy nút thời gian (Sáng/Trưa/Chiều/Tối) đang được chọn (có class bg-blue-600)
    const activeTimeBtn = document.querySelector('.time-btn.bg-blue-600');

    // 2. Validate dữ liệu
    if (!selectThuoc.value) {
        alert("Vui lòng chọn tên thuốc!");
        return;
    }
    if (!inputLieuDung.value || inputLieuDung.value <= 0) {
        alert("Vui lòng nhập liều dùng hợp lệ!");
        return;
    }
    // if (inputSoNgay.value <= 0) {
    //     alert("Vui lòng nhập số ngày hợp lệ!");
    //     return;
    // }

    // 3. Tạo object thuốc
    const thuocItem = {
        id: selectThuoc.value,
        ten_thuoc: selectThuoc.options[selectThuoc.selectedIndex].text.trim(),
        lieu_dung: inputLieuDung.value,
        don_vi: inputDonVi.value,
        so_ngay: inputSoNgay.value,
        buoi_uong: activeTimeBtn ? activeTimeBtn.innerText.trim() : 'Sáng', // Mặc định Sáng nếu ko chọn
        thoi_diem: selectThoiDiem.value || 'Sau ăn' // Mặc định Sau ăn nếu ko chọn
    };

    // 4. Thêm vào mảng
    danhSachThuocKeDon.push(thuocItem);

    // 5. Render lại giao diện
    renderMedicineList();

    // 6. Reset form (tuỳ chọn)
    inputLieuDung.value = '';
    // inputSoNgay.value = ''; // Thường số ngày giữ nguyên thì tiện hơn
    selectThuoc.value = '';
    inputDonVi.value = '';
    document.getElementById('input-han-su-dung').value = ''; // Reset ô hạn sử dụng
}

function renderMedicineList() {
    const container = document.getElementById('list-thuoc-container');
    const listBody = document.getElementById('list-thuoc-body');

    // Nếu không có thuốc nào thì ẩn bảng đi
    if (danhSachThuocKeDon.length === 0) {
        container.classList.add('hidden');
        return;
    }

    container.classList.remove('hidden');
    listBody.innerHTML = ''; // Xóa nội dung cũ

    // Duyệt mảng và tạo HTML
    danhSachThuocKeDon.forEach((thuoc, index) => {
        const rowHtml = `
            <div class="p-4 flex items-start justify-between hover:bg-gray-50 gap-4">
                <div class="flex-1 space-y-2">
                    <p class="text-sm text-gray-900 font-medium">
                        ${index + 1}. ${thuoc.ten_thuoc}
                    </p>

                    <div class="flex flex-wrap items-center gap-2 text-xs text-gray-600">
                        <span class="bg-blue-50 text-blue-700 px-3 py-2 rounded border border-blue-100">
                            ${thuoc.lieu_dung} ${thuoc.don_vi}/lần
                        </span>

                        <span class="text-gray-300">-</span>

                        <span class="bg-gray-100 px-3 py-2 rounded">
                            ${thuoc.buoi_uong}
                        </span>

                        <span class="text-gray-300">-</span>

                        <span class="bg-gray-100 px-3 py-2 rounded">
                            ${thuoc.thoi_diem}
                        </span>

                        <span class="text-gray-300">-</span>

                        <span class="bg-green-50 text-green-700 px-3 py-2 rounded border border-green-100">
                            ${thuoc.so_ngay} ngày
                        </span>
                    </div>
                </div>

                <button
                    type="button"
                    onclick="removeMedicine(${index})"
                    class="text-red-500 hover:text-red-700 hover:bg-red-50 p-2 rounded transition-colors flex-shrink-0"
                    title="Xóa thuốc này"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-trash-2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                </button>
            </div>
        `;
        listBody.insertAdjacentHTML('beforeend', rowHtml);
    });
}

// Hàm xóa thuốc khỏi danh sách
function removeMedicine(index) {
    danhSachThuocKeDon.splice(index, 1); // Xóa phần tử tại index
    renderMedicineList(); // Vẽ lại bảng

}