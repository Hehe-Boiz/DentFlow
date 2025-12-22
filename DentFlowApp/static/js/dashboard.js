// Cấu hình thời gian
const today = new Date();
const currentDay = today.getDate();
const currentMonth = today.getMonth();
const currentYear = today.getFullYear();
const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

// Gọi API
fetch('/manager/statistics')
    .then(response => {
        if (!response.ok) throw new Error('Lỗi tải dữ liệu');
        return response.json();
    })
    .then(result => {
        if (result.status === 'success') {
            // result.data là mảng các hóa đơn từ Python
            renderChart(result.data);
        } else {
            console.error("Lỗi từ server:", result.message);
        }
    })
    .catch(error => console.error("Fetch error:", error));


function renderChart(invoices) {
    // 1. CHUẨN BỊ DỮ LIỆU
    // Tạo mảng "thùng chứa" doanh thu cho từng ngày (Index 1 -> 31)
    // Dùng mảng size 32 để index khớp với ngày (bỏ qua index 0)
    let dailyRevenue = new Array(daysInMonth + 1).fill(0);

    // 2. CỘNG DỒN DOANH THU THEO NGÀY
    invoices.forEach(inv => {
        // Parse ngày từ chuỗi 'YYYY-MM-DD HH:mm:ss' hoặc 'YYYY-MM-DD'
        let date = new Date(inv.ngay_thanh_toan);
        let day = date.getDate();

        // Cộng tiền vào ngày tương ứng
        // Lưu ý: Chia 1.000.000 để biểu đồ hiển thị đơn vị "Triệu đồng" cho gọn
        dailyRevenue[day] += (inv.tong_tien / 1000000);
    });

    // 3. TẠO DATASETS CHO CHART
    const labels = [];
    const dataValues = [];
    const backgroundColors = [];

    for (let i = 1; i <= daysInMonth; i++) {
        labels.push(i);

        // Logic hiển thị: Chỉ hiện data cho quá khứ và hôm nay
        if (i <= currentDay) {
            dataValues.push(dailyRevenue[i]); // Lấy dữ liệu thật từ mảng đã cộng dồn

            // Tô màu
            if (i === currentDay) {
                backgroundColors.push('#123616'); // Hôm nay
            } else {
                backgroundColors.push('#dee2e6'); // Quá khứ
            }
        } else {
            // Tương lai
            dataValues.push(null);
            backgroundColors.push('transparent');
        }
    }

    // 4. VẼ BIỂU ĐỒ (Giữ nguyên cấu hình đẹp của bạn)
    const ctx = document.getElementById("chart-bar-monthly");

    // Hủy biểu đồ cũ nếu có để tránh lỗi vẽ chồng
    if (window.myMonthlyChart) {
        window.myMonthlyChart.destroy();
    }

    window.myMonthlyChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Doanh thu",
                data: dataValues,
                backgroundColor: backgroundColors,
                hoverBackgroundColor: '#123616',
                borderRadius: 3,
                barPercentage: 0.7,
                categoryPercentage: 0.8,
                maxBarThickness: 20
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {display: false},
                tooltip: {
                    callbacks: {
                        title: (context) => `Ngày ${context[0].label}/${currentMonth + 1}`,
                        label: (context) => {
                            // Format lại tiền tệ cho đẹp trong tooltip
                            // context.raw đang là đơn vị Triệu, nhân lại 1tr để hiển thị full số
                            let rawValue = context.raw * 1000000;
                            return `Doanh thu: ${new Intl.NumberFormat('vi-VN', {
                                style: 'currency',
                                currency: 'VND'
                            }).format(rawValue)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    // suggestedMax: 60, // Có thể bỏ để chart tự scale theo dữ liệu thật
                    grid: {
                        borderDash: [5, 5],
                        drawBorder: false,
                        color: "rgba(0,0,0,0.05)"
                    },
                    ticks: {
                        font: {size: 11, family: "'Inter', sans-serif"},
                        callback: function (value) {
                            return value + ' Tr'; // Thêm chữ Tr vào trục Y
                        }
                    }
                },
                x: {
                    grid: {display: false, drawBorder: false},
                    ticks: {
                        font: {size: 11, family: "'Inter', sans-serif"},
                        autoSkip: true,
                        maxRotation: 0,
                        color: (ctx) => ctx.tick.label == currentDay ? '#123616' : '#9aa0ac',
                        font: (ctx) => ctx.tick.label == currentDay ? {weight: 'bold', size: 12} : {size: 11}
                    }
                }
            }
        }
    });

}