const today = new Date();
let currentDay = today.getDate();
const currentMonth = today.getMonth();
const currentYear = today.getFullYear();

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
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {

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


function renderMonthlyChart(invoices, elmId, month) {
    const ctx = document.getElementById(elmId);

    const daysInMonth = new Date(currentYear, month, 0).getDate();
    if (currentMonth + 1 === month) {
        currentDay = today.getDate()
    }

    let dailyRevenue = new Array(daysInMonth + 1).fill(0);

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
    const labels = doctorData.data.map(item => item.ten_bac_si);
    const dataValues = doctorData.data.map(item => item.tong_doanh_thu);
    const baseColors = [
        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
        '#858796', '#5a5c69', '#2e59d9', '#17a673', '#2c9faf'
    ];
    const bgColors = labels.map((_, i) => baseColors[i % baseColors.length]);
    const ctx = document.getElementById("chart-doctors");
    if (!ctx) return;
    if (window.myDoctorChart) window.myDoctorChart.destroy();
    window.myDoctorChart = new Chart(ctx, {
        type: 'doughnut',
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
            cutout: '70%',
        }
    });
}

export default {renderDoanhThuNamNgayLineChart, renderMonthlyChart, renderDoctorChart, currentMonth}