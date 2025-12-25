// DOANH THU THEO THÁNG
// === CẤU HÌNH CHUNG ===
const today = new Date();
let currentDay = today.getDate();
const currentMonth = today.getMonth();
const currentYear = today.getFullYear();


function renderMonthlyChart(invoices, elmId, month) {
    const ctx = document.getElementById(elmId);

    const daysInMonth = new Date(currentYear, month, 0).getDate();
    if (currentMonth + 1 === month) {
        currentDay = today.getDate()
    }

    let dailyRevenue = new Array(daysInMonth + 1).fill(0);
    // console.log('invoice', invoices)
    invoices.forEach(inv => {
        let date = new Date(inv.ngay_thanh_toan);
        let day = date.getDate();
        dailyRevenue[day] += (inv.tong_tien / 1000000);
    });
    console.log(dailyRevenue)
    const labels = [];
    const dataValues = [];
    const backgroundColors = [];

    const config = {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Doanh thu",
                data: dataValues,
                backgroundColor: backgroundColors,
                hoverBackgroundColor: '#1757ef',
                borderRadius: 3,
                barPercentage: 0.7,
                categoryPercentage: 0.8,
                maxBarThickness: 20
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {mode: 'index', intersect: false},
            plugins: {
                legend: {display: false},
                tooltip: {
                    callbacks: {
                        title: (context) => `Ngày ${context[0].label}/${month}`,
                        label: (context) => {
                            let rawValue = context.raw * 1000000;
                            return `Doanh thu: ${new Intl.NumberFormat('vi-VN', {
                                style: 'currency', currency: 'VND'
                            }).format(rawValue)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {borderDash: [5, 5], drawBorder: false, color: "rgba(0,0,0,0.05)"},
                    ticks: {
                        font: {size: 11, family: "'Inter', sans-serif"},
                        callback: function (value) {
                            return value + ' Tr';
                        }
                    }
                },
                x: {
                    grid: {display: false},
                    ticks: {
                        autoSkip: true,
                        maxRotation: 0,
                        color: (ctx) => ctx.tick.label == currentDay ? '#123616' : '#9aa0ac',
                        font: (ctx) => ctx.tick.label == currentDay ? {
                            weight: 'bold',
                            size: 12
                        } : {size: 11}
                    }
                }
            }
        }
    };
    for (let i = 1; i <= daysInMonth; i++) {
        labels.push(i);
        if (i <= currentDay) {
            dataValues.push(dailyRevenue[i]);
            backgroundColors.push(i === currentDay ? '#17a673' : '#4e73df');
        } else {
            dataValues.push(null);
            backgroundColors.push('transparent');
        }
    }

    if (ctx) {
        if (Chart.getChart(ctx)) {
            Chart.getChart(ctx).destroy()
        }
        new Chart(ctx, config)
    }

}

function renderDoctorChart(doctorData) {
    const labels = doctorData.map(item => item.ten_bac_si);
    const dataValues = doctorData.map(item => item.tong_doanh_thu);
    const baseColors = [
        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
        '#858796', '#5a5c69', '#2e59d9', '#17a673', '#2c9faf'
    ];
    const bgColors = labels.map((_, i) => baseColors[i % baseColors.length]);
    const ctx = document.getElementById("chart-doctors");
    if (!ctx) return;
    if (window.myDoctorChart) window.myDoctorChart.destroy();
    window.myDoctorChart = new Chart(ctx, {
        type: 'doughnut', // Biểu đồ vành khuyên
        data: {
            labels: labels,
            datasets: [{
                data: dataValues,
                backgroundColor: bgColors,
                hoverBorderColor: "rgba(234, 236, 244, 1)",
                hoverOffset: 4
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {usePointStyle: true, padding: 20, font: {family: "'Inter', sans-serif"}}
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.label || '';
                            if (label) label += ': ';
                            let value = context.raw;
                            label += new Intl.NumberFormat('vi-VN', {
                                style: 'currency', currency: 'VND'
                            }).format(value);
                            return label;
                        }
                    }
                }
            },
            cutout: '70%', // Độ mỏng của vòng tròn
        }
    });
}


async function fetchMonthly() {
    const respone = await fetch('/manager/statistics/monthly')
    const result = await respone.json()
    if (result.status !== 'success' && result.status !== 'ok') {
        console.error("Lỗi dữ liệu:", result);
    } else {
        return result.data
    }
}

async function fetchDoctors(month) {
    try {
        const response = await fetch(`/manager/statistics/doctors?month=${month}`);
        const result = await response.json()
        if (result.status !== 'success') {
            console.error("Lỗi dữ liệu:", result);
        } else {
            console.log('Data daily', result.data_daily)
            return result
        }
    } catch (error) {
        console.error('Lỗi hệ thống:', error);
        return 0;
    }
}

document.addEventListener("DOMContentLoaded", async function () {
    try {
        const dataMonthly = await fetchMonthly()
        const data = await fetchDoctors()
        const dataDoctor = data.data
        renderMonthlyChart(dataMonthly, "chart-bar-monthly", currentMonth)
        renderDoctorChart(dataDoctor)

        const tbody = document.getElementById('table-body');
        // Tính tổng doanh thu để chia phần trăm (nếu API chưa trả về)
        const totalRevenue = dataDoctor.reduce((sum, item) => sum + item.tong_doanh_thu, 0);

        let html = '';
        dataDoctor.forEach(bs => {
            let phanTram = totalRevenue > 0 ? (bs.tong_doanh_thu / totalRevenue * 100).toFixed(1) : 0;
            const formatMoney = (amount) => {
                return new Intl.NumberFormat('vi-VN', {style: 'currency', currency: 'VND'}).format(amount);
            };
            html += `
                        <tr>
                            <td>${bs.ten_bac_si}</td>
                            <td>${bs.so_luot_kham}</td>
                            <td>${formatMoney(bs.tong_doanh_thu)}</td>
                            <td>${formatMoney(bs.trung_binh_kham)}</td>
                            <td>
                                <div style="display: flex; align-items: center;">
                                    <span style="margin-right: 8px;">${phanTram}%</span>
                                    <div style="flex-grow: 1; background: #eee; height: 6px; border-radius: 3px;">
                                        <div style="width: ${phanTram}%; background: #008a75; height: 100%; border-radius: 3px;"></div>
                                    </div>
                                </div>
                            </td>
                        </tr>
                        `;
        });
        tbody.innerHTML = html;
    } catch (err) {
        console.error(err)
    }
});