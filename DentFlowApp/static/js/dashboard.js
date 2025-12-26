document.addEventListener("DOMContentLoaded", async function () {
    try {
        const module = await import('./thongkeFetch.js');
        const {fetchMonthly, fetchDoctors} = module.default
        const dataMonthly = await fetchMonthly()
        const data = await fetchDoctors()
        const dataDoctor = data
        const moduleRender = await import('./thonkeRenderChart.js')
        const {renderMonthlyChart, renderDoctorChart, currentMonth} = moduleRender.default
        renderMonthlyChart(dataMonthly, "chart-bar-monthly", currentMonth)
        renderDoctorChart(dataDoctor)

        const tbody = document.getElementById('table-body');

        const totalRevenue = dataDoctor.data.reduce((sum, item) => sum + item.tong_doanh_thu, 0);

        let html = '';
        dataDoctor.data.forEach(bs => {
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