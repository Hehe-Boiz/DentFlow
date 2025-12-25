import {formatCurrency} from "./utils.js";

let danhSachThuocKeDon = [];
let totalAmount = 0;
let stt = 0;

export function initCreateTreatment() {

    danhSachThuocKeDon = [];
    totalAmount = 0;
    stt = 0;

    const btn = document.getElementById("btn-ke-don");
    const container = document.getElementById("ke-don-container");
    let loaded = false;

    if (btn) {
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);

        newBtn.addEventListener("click", async () => {
            if (loaded) {
                container.classList.toggle("hidden");
                return;
            }
            try {
                const res = await fetch("/treatments/ke-don");
                const html = await res.text();
                container.innerHTML = html;
                loaded = true;

                initTimeButtons();
                checkLoThuoc();
                inputUnit();
                initAddMedicineEvent();
                initDeleteMedicineEvent();
            } catch (err) {
                console.error("Lỗi tải form kê đơn", err);
            }
        });
    }

    initServiceEvents();
    initSaveTreatmentEvent();
}

function inputUnit() {
    const thuocSelect = document.getElementById('select-ten-thuoc');
    const unitInput = document.getElementById('input-don-vi');

    if (thuocSelect && unitInput) {
        thuocSelect.addEventListener('change', function () {
            const selectedOption = this.options[this.selectedIndex];
            const unit = selectedOption.getAttribute('data-unit');
            console.log(unit);

            unitInput.value = unit || "viên";
        });
    }
}



function initServiceEvents() {
    const serviceSelect = document.getElementById('service-select');
    const priceInput = document.getElementById('service-price');
    const noteInput = document.getElementById('service-note');
    const btnAdd = document.getElementById('btn-add-service');
    const tableBody = document.getElementById('service-table-body');
    const totalDisplay = document.getElementById('total-amount');
    const listContainer = document.getElementById('service-list-container');


    const updatePrice = () => {
        if (serviceSelect && priceInput) {
            const selectedOption = serviceSelect.options[serviceSelect.selectedIndex];
            const price = selectedOption ? selectedOption.getAttribute('data-price') : 0;
            priceInput.value = price || 0;
        }
    };

    if (serviceSelect && priceInput) {
        serviceSelect.addEventListener('change', updatePrice);
    }

    if (btnAdd) {
        btnAdd.addEventListener('click', function () {


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

            stt++;
            totalAmount += price;

            const row = document.createElement('tr');
            listContainer.classList.remove('hidden');
            row.dataset.serviceId = serviceId
            row.className = "hover:bg-gray-50 transition-colors";
            row.innerHTML = `
                <td class="py-3 px-4 text-sm">${stt}</td>
                <td class="py-3 px-4 text-sm text-gray-900">${serviceName}</td>
                <td class="py-3 px-4 text-sm text-emerald-700 font-medium" data-price="${price}">${formatCurrency(price)}</td>
                <td class="py-3 px-4 text-sm text-gray-600">${note}</td>
                <td class="py-3 px-4">
                    <button type="button" class="btn-delete text-red-600 hover:text-red-800 p-2 rounded" data-price="${price}">
                        <i class="fa-regular fa-trash-can"></i>
                    </button>
                </td>
            `;

            tableBody.appendChild(row);

            totalDisplay.innerText = formatCurrency(totalAmount);

            row.querySelector('.btn-delete').addEventListener('click', function () {
                const priceToRemove = parseFloat(this.getAttribute('data-price'));
                totalAmount -= priceToRemove;

                totalDisplay.innerText = formatCurrency(totalAmount);

                row.remove();

                const rows = tableBody.querySelectorAll('tr');
                stt = rows.length;
                rows.forEach((r, index) => {
                    r.querySelector('td:first-child').innerText = index + 1;
                });

                if (rows.length === 0) {
                    listContainer.classList.add('hidden');
                    stt = 0;
                    totalAmount = 0;
                }
            });

            serviceSelect.value = "";
            priceInput.value = 0;
            noteInput.value = "";

        });
        if (serviceSelect && serviceSelect.value) {
            updatePrice();
            btnAdd.click();
        }
    }
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

        warningBox.classList.add('hidden');
        inputHanSuDung.value = '';
        inputHanSuDung.classList.remove('text-red-600', 'font-bold');


        if (soNgay <= 0) {
            return;
        }

        inputHanSuDung.value = "Đang tìm kiếm...";

        fetch(`/treatment/thuoc/${thuocId}/lo-phu-hop`, {
            method: 'POST', headers: {
                'Content-Type': 'application/json',
            }, body: JSON.stringify({so_ngay_dung: soNgay})
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const lo = data.data;
                    inputHanSuDung.value = `${lo.han_su_dung} (Lô: ${lo.so_lo})`;
                    inputHanSuDung.classList.remove('text-red-600');
                    inputHanSuDung.classList.add('text-green-700');
                } else {
                    inputHanSuDung.value = "Không khả dụng";
                    inputHanSuDung.classList.add('text-red-600', 'font-bold');

                    warningText.innerText = data.message || "Không tìm thấy lô thuốc phù hợp.";
                    warningBox.classList.remove('hidden');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                inputHanSuDung.value = "Lỗi kiểm tra";
            });
    }

    function handleInput() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(fetchLoThuocPhuHop, 500);
    }

    selectThuoc.addEventListener('change', fetchLoThuocPhuHop);
    inputSoNgay.addEventListener('input', handleInput);

}



function initAddMedicineEvent() {
    const btnThemThuoc = document.getElementById('id-add-thuoc'); // Nút thêm thuốc

    if (btnThemThuoc) {
        const newBtn = btnThemThuoc.cloneNode(true);
        btnThemThuoc.parentNode.replaceChild(newBtn, btnThemThuoc);

        newBtn.addEventListener('click', function () {
            handleAddMedicine();
        });
    }
}


function handleAddMedicine() {
    const selectThuoc = document.getElementById('select-ten-thuoc');
    const inputLieuDung = document.querySelector('input[type="number"][placeholder="2"]'); // Input Liều dùng
    const inputDonVi = document.getElementById('input-don-vi');
    const inputSoNgay = document.getElementById('input-so-ngay');
    const selectThoiDiem = document.getElementById('select-thoi-diem');
    const inputGhiChu = document.getElementById('ghi-chu-thuoc');

    const activeTimeBtn = document.querySelector('.time-btn.bg-blue-600');

    if (!selectThuoc.value) {
        alert("Vui lòng chọn tên thuốc!");
        return;
    }
    if (!inputLieuDung.value || inputLieuDung.value <= 0) {
        alert("Vui lòng nhập liều dùng hợp lệ!");
        return;
    }

    const thuocItem = {
        id: selectThuoc.value,
        ten_thuoc: selectThuoc.options[selectThuoc.selectedIndex].text.trim(),
        lieu_dung: inputLieuDung.value,
        don_vi: inputDonVi.value,
        so_ngay: inputSoNgay.value,
        buoi_uong: activeTimeBtn ? activeTimeBtn.innerText.trim() : '',
        thoi_diem: selectThoiDiem.value,
        ghi_chu: inputGhiChu.value,
    };

    danhSachThuocKeDon.push(thuocItem);

    renderMedicineList();

    inputLieuDung.value = '';
    selectThuoc.value = '';
    inputDonVi.value = '';
    document.getElementById('input-han-su-dung').value = '';
}

function renderMedicineList() {
    const container = document.getElementById('list-thuoc-container');
    const listBody = document.getElementById('list-thuoc-body');

    if (danhSachThuocKeDon.length === 0) {
        container.classList.add('hidden');
        return;
    }

    container.classList.remove('hidden');
    listBody.innerHTML = '';

    danhSachThuocKeDon.forEach((thuoc, index) => {
        const parts = [];

        if (thuoc.lieu_dung && thuoc.don_vi) {
            parts.push(`
        <span class="bg-blue-50 text-blue-700 px-3 py-2 rounded border border-blue-100">
            ${thuoc.lieu_dung} ${thuoc.don_vi}/lần
        </span>
    `);
        }

        if (thuoc.buoi_uong) {
            parts.push(`
        <span class="bg-gray-100 px-3 py-2 rounded">
            ${thuoc.buoi_uong}
        </span>
    `);
        }

        if (thuoc.thoi_diem) {
            parts.push(`
        <span class="bg-gray-100 px-3 py-2 rounded">
            ${thuoc.thoi_diem}
        </span>
    `);
        }

        if (thuoc.so_ngay) {
            parts.push(`
        <span class="bg-green-50 text-green-700 px-3 py-2 rounded border border-green-100">
            ${thuoc.so_ngay} ngày
        </span>
    `);
        }

        if (thuoc.ghi_chu) {
            parts.push(`
        <span class="bg-yellow-50 text-yellow-700 px-3 py-2 rounded border border-yellow-100">
            ${thuoc.ghi_chu}
        </span>
    `);
        }

        const infoHtml = parts.join(`
    <span class="text-gray-300">-</span>`);
        const rowHtml = `
            <div class="p-4 flex items-start justify-between hover:bg-gray-50 gap-4">
                <div class="flex-1 space-y-2">
                    <p class="text-sm text-gray-900 font-medium">
                        ${index + 1}. ${thuoc.ten_thuoc}
                    </p>
        
                    <div class="flex flex-wrap items-center gap-2 text-xs text-gray-600">
                        ${infoHtml}
                    </div>
                </div>
        
                <button
                    type="button"
                    class="btn-remove-medicine text-red-500 hover:text-red-700 hover:bg-red-50 p-2 rounded transition-colors flex-shrink-0"
                    data-index="${index}"
                    title="Xóa thuốc này"
                >
                                            <i class="fa-regular fa-trash-can"></i>

                </button>
            </div>
        `;


        listBody.insertAdjacentHTML('beforeend', rowHtml);
    });
}

function removeMedicine(index) {
    danhSachThuocKeDon.splice(index, 1);
    renderMedicineList();
}

function initDeleteMedicineEvent() {
    const listBody = document.getElementById('list-thuoc-body');
    if (listBody) {
        listBody.addEventListener('click', function (e) {
            const btn = e.target.closest('.btn-remove-medicine');

            if (btn) {
                const index = btn.getAttribute('data-index');
                if (index !== null) {
                    removeMedicine(parseInt(index));
                }
            }
        });
    }
}


function initSaveTreatmentEvent() {
    const btnSaveTreatment = document.getElementById('btn-save-treatment');
    btnSaveTreatment.addEventListener('click', async function () {
        const selectPatientElement = document.querySelector('select[name="patient_id"]')
        const patientId = selectPatientElement ? selectPatientElement.value : null;
        const selectedOption = selectPatientElement.options[selectPatientElement.selectedIndex];
        const lichHenId = selectedOption ? selectedOption.getAttribute('data-lichhenId') : null;

        if (!patientId) {
            alert("Vui lòng chọn lịch khám/bệnh nhân trước khi lưu!");
            selectPatientElement.focus();
            return;
        }

        const chanDoanInput = document.querySelector('textarea[name="chan_doan"]');
        const chanDoan = chanDoanInput ? chanDoanInput.value : "";

        if (chanDoan === "") {
            alert("Vui lòng nhập chẩn đoán");
            chanDoanInput.focus();
            return;
        }

        const ghiChuInput = document.querySelector('textarea[name="ghi-chu-chu-y"]');
        const ghiChu = ghiChuInput ? ghiChuInput.value : "";

        const services = [];
        const containerServices = document.getElementById("service-list-container")
        if (!containerServices.classList.contains("hidden")) {
            const rows = document.querySelectorAll('#service-table-body tr');

            rows.forEach(row => {
                const sId = row.getAttribute('data-service-id');
                const priceCell = row.querySelector('td[data-price]');
                const sPrice = priceCell ? priceCell.getAttribute('data-price') : 0;

                if (sId) services.push({id: sId, price: parseFloat(sPrice)});
            });
        }

        try {
            const originalText = btnSaveTreatment.innerText;
            btnSaveTreatment.innerText = "Đang xử lý...";
            btnSaveTreatment.disabled = true;

            const response = await fetch('/treatment', {
                method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({
                    patient_id: patientId,
                    chan_doan: chanDoan,
                    ghi_chu: ghiChu,
                    services: services,
                    medicines: danhSachThuocKeDon,
                    lich_hen_id: lichHenId
                })
            });

            const result = await response.json();

            if (result.status === 'success') {
                alert("Tạo phiếu thành công!");
                window.location.reload();
                selectPatientElement.value = ""
                chanDoanInput.value = ""
                ghiChuInput.value = ""

            } else {
                alert("Lỗi: " + result.message);
            }

        } catch (error) {
            console.error(error);
            alert("Lỗi kết nối server");
        } finally {
            btnSaveTreatment.innerText = "Lưu phiếu điều trị";
            btnSaveTreatment.disabled = false;
        }
    })
}