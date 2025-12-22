document.addEventListener("DOMContentLoaded", function () {
    fetch('/api/doanh-thu-theo-ngay')
        .then(response => response.json())
        .then(data => {
            drawChart(data);
        })
        .catch(error => console.error('Lỗi tải dữ liệu:', error));
});

function drawChart(apiData) {
    const ctx = document.getElementById('myChart');

    new Chart(ctx, {
        type: 'bar', // Loại biểu đồ: 'bar' (cột), 'line' (đường), 'pie' (tròn)
        data: {
            labels: apiData.labels, // Nhãn ngày từ server gửi về
            datasets: [{
                label: 'Doanh thu (VNĐ)',
                data: apiData.values, // Số tiền từ server gửi về
                backgroundColor: '#0d6efd', // Màu xanh dương giống theme của bạn
                borderRadius: 4,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        // Format tiền tệ cho đẹp (VD: 1.000.000)
                        callback: function (value) {
                            return value.toLocaleString('vi-VN') + ' ₫';
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return context.raw.toLocaleString('vi-VN') + ' ₫';
                        }
                    }
                }
            }
        }
    });
}