function toggleFilter() {
    const selectBacsiTheoThang = document.getElementById('select-bacsi-thang')
    const monthIndex = new Date().getMonth() + 1;
    if (selectBacsiTheoThang) {
        selectBacsiTheoThang.value = monthIndex
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
    const spanNav = document.getElementsByClassName('dot');
    for (let i = 0; i < spanNav.length; i++) {
        spanNav[i].classList.remove('active');

        if (i === page) {
            spanNav[i].classList.add('active');
        }
    }
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
        if (currentPage > 0) {

            currentPage--;
            renderCTHD(paginateList, currentPage);
            updateButtons();
        }
    })
    btnNext.addEventListener('click', () => {
        if (currentPage < totalPages - 1) {

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
    const module = await import('./thongkeFetch.js');
    const moduleRender = await import('./thonkeRenderChart.js');

    const {fetchCTHD, fetchDoanhThuTheoThang, fetchDoctors, fetchDoanhThuTrongNamNgay} = module.default;

    const data = await fetchCTHD(monthSelect.value)
    const divPaginate = document.getElementById('paginate-numb-cthd');

    let [paginateList, totalPages] = doChiTietHoaDon(data);
    let html = `<button id="paginate-btn-prev-cthd" class="btn btn-sm btn-secondary"> < </button>`;
    for (let i = 0; i < totalPages; i++) {

        html += `
        <span class="p-2 mx-1 border rounded dot" style="cursor: pointer;">
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
            const data_doanhthu_thang = await fetchDoanhThuTheoThang(month);
            const doanh_thu = data_doanhthu_thang.reduce((total, item) => total + item.tong_tien, 0)
            const {renderMonthlyChart} = moduleRender.default;
            renderMonthlyChart(data_doanhthu_thang, 'monthly-chart', month);

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

                const {renderMonthlyChart} = moduleRender.default;
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

        const {renderDoanhThuNamNgayLineChart} = moduleRender.default;

        renderDoanhThuNamNgayLineChart(resDataNam);

    } catch (err) {
        console.error("Lỗi khởi tạo:", err);
    }
})