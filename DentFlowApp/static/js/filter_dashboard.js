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

    const module = await import('./thongKeFetch.js');
    const moduleRender = await import('./thongKeRender.js');
    const selectFilter = document.getElementById('select-filter');
    const divBacSi = document.getElementById('div_theo_bacsi');
    const divThang = document.getElementById('div_theo_thang');
    const monthSelect = document.getElementById('select-thang');
    const bacsiSelect = document.getElementById('select-bacsi');
    const spanMonth = document.getElementById('span-slected-month');
    const spanDoanhThu = document.getElementById('span-tong-doanh-thu');
    const tbody = document.getElementById('table-body-cthd');
    const divDoctorChart = document.getElementById('doctor-chart');
    const divMonthlyChart = document.getElementById('monthly-chart');
    if (selectFilter.value === 'select-thang') {
        divThang.style.display = 'block';
        divBacSi.style.display = 'none';
        console.log('type', selectFilter.value)

    }
    if (selectFilter.value === 'select-bacsi') {
        divThang.style.display = 'none';
        divBacSi.style.display = 'block';
        divDoctorChart.style.display = 'block';
        divMonthlyChart.style.display = 'none';
        console.log('type', selectFilter.value)

    }
    selectFilter.addEventListener('change', () => {
        if (selectFilter.value === 'select-thang') {
            divThang.style.display = 'block';
            divBacSi.style.display = 'none';
            divDoctorChart.style.display = 'none';
            divMonthlyChart.style.display = 'block';
            console.log('type', selectFilter.value)

        }
        if (selectFilter.value === 'select-bacsi') {
            divThang.style.display = 'none';
            divBacSi.style.display = 'block';
            console.log('type', selectFilter.value)

        }
    })

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN').format(amount) + ' đ';
    };

    const {fetchDoanhThuMonthlyOnly, fetchDoctorOnly} = module.default;
    const {renderDoanhThuMonthonly, renderDoctorBarChart} = moduleRender.default


    async function updateDashboardData(month, bacsi) {
        if (!month || month === "0") return;
        try {
            if (month != null) {
                const dataMonthly = await fetchDoanhThuMonthlyOnly(month)
                renderDoanhThuMonthonly(dataMonthly)
                spanMonth.textContent = month
                let tongDoanhThu = dataMonthly.data.reduce((tong, item) => {
                    return tong + (item.doanh_thu || 0)
                }, 0)
                console.log('ne', tongDoanhThu)
                spanDoanhThu.textContent = formatCurrency(0)
                if (tongDoanhThu) {
                    spanDoanhThu.textContent = formatCurrency(tongDoanhThu);
                }
            }
            if (bacsi != null) {
                const dataDoctor = await fetchDoctorOnly(bacsi);
                console.log('ne-doctor', dataDoctor)
                renderDoctorBarChart(dataDoctor);
            }

        } catch (e) {
            console.error("Lỗi cập nhập dashboard", e)
        }
    }

    console.log('month here!')
    monthSelect.addEventListener('change', async (event) => {
        const selectedMonth = event.target.value;
        console.log(selectedMonth)
        await updateDashboardData(selectedMonth, null)
    })
    bacsiSelect.addEventListener('change', async (event) => {
        const selectedBacSi = event.target.value;
        await updateDashboardData(null, selectedBacSi)
    })

})