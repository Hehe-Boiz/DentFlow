async function exportToCSV() {
    const month = document.getElementById('select-bacsi-thang').value;
    if (!month) {
        alert("Vui lòng chọn tháng!");
        return;
    }

    try {
        const response = await fetch(`/manager/statistics/monthly?month=${month}`);
        const result = await response.json();

        if (result.status !== 'success') {
            alert("Lỗi: " + (result.message || "Không lấy được dữ liệu"));
            return;
        }

        const dataList = result.data_ds_hoadon;

        if (!dataList || dataList.length === 0) {
            alert("Không có dữ liệu hóa đơn trong tháng này.");
            return;
        }

        const headers = ["Ngày thanh toán", "Họ tên bệnh nhân", "Dịch vụ", "Thuốc", "Tổng tiền"];

        const rows = dataList.map(item => {
            const strDichVu = item.ds_dv ? item.ds_dv.join('; ') : '';
            const strThuoc = item.ds_t ? item.ds_t.join('; ') : '';

            return [
                `"${item.ngay_thanh_toan}"`,
                `"${item.ho_ten}"`,
                `"${strDichVu}"`,
                `"${strThuoc}"`,
                `${item.tong_tien}`
            ];
        });


        const csvContent = "\uFEFF" + [headers, ...rows]
            .map(e => e.join(","))
            .join("\n");

        const blob = new Blob([csvContent], {type: 'text/csv;charset=utf-8;'});
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.setAttribute("href", url);
        link.setAttribute("download", `thong_ke_thang_${month}.csv`);
        link.style.visibility = 'hidden';

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

    } catch (error) {
        console.error('Lỗi khi xuất CSV:', error);
        alert("Đã xảy ra lỗi khi tải dữ liệu.");
    }
}