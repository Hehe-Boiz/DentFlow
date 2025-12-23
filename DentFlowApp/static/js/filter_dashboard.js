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
            label: 'Doanh thu 5 ngày gần đây',
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
                legend: {position: 'top'},
                title: {display: true, text: 'Biểu đồ doanh thu theo ngày'},
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

async function fetchCTHD() {
    const respone = await fetch('/manager/statistics/daily-recently');
    let result = await respone.json()
    if (result.status !== 'success' && result.status !== 'ok') {
        console.error("Lỗi dữ liệu:", result);

    } else {
        return result.data
    }
}

async function fetchDoanhThuTheoThang(month) {
    try {
        const response = await fetch(`/manager/statistics/monthly?month=${month}`);
        const data = await response.json();
        if (data.status === 'success') {
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

document.addEventListener("DOMContentLoaded", async function () {
    toggleFilter()
    const monthSelect = document.getElementById('select-bacsi-thang')
    const bacsiSelect = document.getElementById('select-bacsi')
    const spanMonth = document.getElementById('span-slected-month')
    const spanDoanhThu = document.getElementById('span-tong-doanh-thu')
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN').format(amount) + ' đ';
    };

    async function updateDashboardData(month) {
        if (!month || month === "0") return;
        try {
            const doanh_thu = await fetchDoanhThuTheoThang(month);
            spanMonth.textContent = month
            console.log(doanh_thu)
            if (doanh_thu) {
                spanDoanhThu.textContent = formatCurrency(doanh_thu)
            }
            const resultDoctors = await fetchDoctors()
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
    bacsiSelect.addEventListener('change', (event) => {
        const selectedBacSi = event.target.value;
        if (selectedBacSi !== "0") {
            if (cachedDoctorData.daily && cachedDoctorData.daily[selectedBacSi]) {
                const doctorData = cachedDoctorData.daily[selectedBacSi];
                renderMonthlyChart(doctorData, 'monthly-chart', monthSelect.value)
            }
        } else {
            console.warn("Không có dữ liệu chi tiết cho bác sĩ này");
        }
    })
    try {
        if (monthSelect.value !== "0") {
            await updateDashboardData(monthSelect.value);
        }

        const resDataNam = await fetchDoanhThuTrongNamNgay();
        renderDoanhThuNamNgayLineChart(resDataNam);

    } catch (err) {
        console.error("Lỗi khởi tạo:", err);
    }

})