function toggleFilter() {
    const selectBacsiTheoThang = document.getElementById('select-bacsi-thang')
    const monthIndex = new Date().getMonth() + 1;
    if (selectBacsiTheoThang) {
        selectBacsiTheoThang.value = monthIndex
    }

}

function renderDoanhThuNamNgayLineChart(resData) {
    const data = {
        labels: Object.values(resData).map(item => item.ngay_thanh_toan),
        datasets: [{
            label: '',
            data: Object.values(resData).map(item => item.doanh_thu),
            fill: true,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.3,
            borderWidth: 2
        }]
    }
    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: false,
                title: {display: false},
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('vi-VN', {
                                    style: 'currency',
                                    currency: 'VND'
                                }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true, // Nên bắt đầu từ 0 để biểu đồ trung thực
                    ticks: {
                        callback: function (value) {
                            // Format trục Y thành tiền tệ
                            return new Intl.NumberFormat('vi-VN', {
                                style: 'currency',
                                currency: 'VND',
                                maximumSignificantDigits: 3
                            }).format(value);
                        }
                    }
                }
            }

        }

    }
    const ctx = document.getElementById('myLineChart')
    if (ctx) {
        if (Chart.getChart(ctx)) {
            Chart.getChart(ctx).destroy()
        }
        new Chart(ctx, config)
    }


}


async function fetchDoanhThuTrongNamNgay() {
    const respone = await fetch('/manager/statistics/daily-recently');
    let result = await respone.json()
    if (result.status !== 'success' && result.status !== 'ok') {
        console.error("Lỗi dữ liệu:", result);

    } else {
        return result.data
    }
}

async function fetchCTHD(month) {
    const respone = await fetch(`/manager/statistics/monthly?month=${month}`);
    let result = await respone.json()
    if (result.status !== 'success') {
        console.error("Lỗi dữ liệu:", result);
    } else {
        return result.data_ds_hoadon
    }
}

async function fetchDoanhThuTheoThang(month) {
    try {
        const response = await fetch(`/manager/statistics/monthly?month=${month}`);
        const data = await response.json();
        if (data.status === 'success') {
            console.log('fetch', data.data)
            renderMonthlyChart(data.data, 'monthly-chart', month);
            return data.data.reduce((total, item) => total + item.tong_tien, 0)
        }
        console.error("Lỗi API:", data.message);
        return 0;
    } catch (error) {
        console.error('Lỗi hệ thống:', error);
        return 0;
    }
}

let cachedDoctorData = {
    daily: {}
}


function doChiTietHoaDon(data, PAGE_SIZE = 10) {

    let html = '';
    const tbody = document.getElementById('table-body-cthd');
    const paginationDiv = document.getElementById('pagination-controls');
    const divPagination = document.getElementById('pagination-controls');

    let paginateList = {}
    let rowPerPage = data.length / PAGE_SIZE
    let pageIndex = 0;
    let totalPages = Math.ceil(data.length / PAGE_SIZE);
    for (let i = 0; i < data.length; i += PAGE_SIZE) {
        paginateList[pageIndex] = data.slice(i, i + PAGE_SIZE);
        pageIndex++;
    }

    return [paginateList, rowPerPage]
}

function renderCTHD(paginateList, page, PAGE_SIZE = 10) {
    let tb_body = document.getElementById('table-body-cthd')
    let html = '';
    for (let j = 0; j < paginateList[page].length; j++) {
        html += `
            <tr>
                <td>${paginateList[page][j]['ngay_thanh_toan']}</td>
                <td>${paginateList[page][j]['ho_ten']}</td>
                <td>${paginateList[page][j]['ds_dv']}</td>
                <td>${paginateList[page][j]['ds_t']}</td>
                <td>
                    <div style="display: flex; align-items: center;">
                                <span id="cthd-tong-tien" style="font-weight: bold; color: green;">
                                    ${paginateList[page][j]['tong_tien'] ? paginateList[page][j]['tong_tien'].toLocaleString() : 0} VNĐ
                                </span>
                    </div>
                </td>
            </tr>
    `
    }
    tb_body.innerHTML = html;
}

function paginateCTHD(paginateList, totalPages) {
    const btnPrev = document.getElementById('paginate-btn-prev-cthd');
    const btnNext = document.getElementById('paginate-btn-next-cthd');
    let currentPage = 0;
    const updateButtons = () => {
        btnPrev.disabled = currentPage === 0;
        btnNext.disabled = currentPage === totalPages - 1;
    };
    updateButtons();
    btnPrev.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderCTHD(paginateList, currentPage);
            updateButtons();
        }
    })
    btnNext.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            renderCTHD(paginateList, currentPage);
            updateButtons();
        }
    })
}

document.addEventListener("DOMContentLoaded", async function () {
    toggleFilter()

    const monthSelect = document.getElementById('select-bacsi-thang')
    const bacsiSelect = document.getElementById('select-bacsi')
    const spanMonth = document.getElementById('span-slected-month')
    const spanDoanhThu = document.getElementById('span-tong-doanh-thu')
    const tbody = document.getElementById('table-body-cthd');

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN').format(amount) + ' đ';
    };

    const data = await fetchCTHD(monthSelect.value)
    const divPaginate = document.getElementById('paginate-numb-cthd');

    let [paginateList, totalPages] = doChiTietHoaDon(data);
    let html = `<button id="paginate-btn-prev-cthd" class="btn btn-sm btn-secondary"> < </button>`;
    for (let i = 0; i < totalPages; i++) {
        html += `
        <span class="p-2 mx-1 border rounded" style="cursor: pointer;">
            ${i + 1}
        </span>
    `;
    }
    html += `<button id="paginate-btn-next-cthd" class="btn btn-sm btn-secondary"> > </button>`;
    divPaginate.innerHTML = html;
    renderCTHD(paginateList, 0);
    paginateCTHD(paginateList, totalPages);


    async function updateDashboardData(month) {
        if (!month || month === "0") return;
        try {
            const doanh_thu = await fetchDoanhThuTheoThang(month);
            spanMonth.textContent = month
            console.log(doanh_thu)
            spanDoanhThu.textContent = formatCurrency(0)
            if (doanh_thu) {
                spanDoanhThu.textContent = formatCurrency(doanh_thu)
            }

            const resultDoctors = await fetchDoctors(monthSelect.value)
            if (resultDoctors && resultDoctors.data_daily) {
                cachedDoctorData.daily = resultDoctors.data_daily
                bacsiSelect.value = "0"
            }
        } catch (e) {
            console.error("Lỗi cập nhập dashboard", e)
        }
    }


    monthSelect.addEventListener('change', async (event) => {
        const selectedMonth = event.target.value;
        await updateDashboardData(selectedMonth)
    })
    bacsiSelect.addEventListener('change', async (event) => {
        const selectedBacSi = event.target.value;
        if (selectedBacSi !== "0") {
            if (cachedDoctorData.daily && cachedDoctorData.daily[selectedBacSi]) {
                const doctorData = cachedDoctorData.daily[selectedBacSi];
                console.log(monthSelect.value)
                renderMonthlyChart(doctorData, 'monthly-chart', monthSelect.value)

            }
        } else {
            await updateDashboardData(monthSelect.value)

            console.warn("Không có dữ liệu chi tiết cho bác sĩ này");
        }
    })
    try {
        if (monthSelect.value !== "0") {
            await updateDashboardData(monthSelect.value);
        }

        const resDataNam = await fetchDoanhThuTrongNamNgay();
        const data_monthly = await fetchCTHD(monthSelect.value)

        renderDoanhThuNamNgayLineChart(resDataNam);

    } catch (err) {
        console.error("Lỗi khởi tạo:", err);
    }
})