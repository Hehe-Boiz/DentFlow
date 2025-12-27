document.addEventListener("DOMContentLoaded", async function () {
    try {
        const module = await import('./thongKeFetch.js');
        const {fetchDoanhThuMonthlyOnly, fetchDoanhThuGanDay, fetchDoctorOnly} = module.default
        const dataMonthlonly = await fetchDoanhThuMonthlyOnly()
        const dataRecently = await fetchDoanhThuGanDay()
        const moduleRender = await import('./thongKeRender.js')
        const dataDoctor = await fetchDoctorOnly()
        const {renderDoanhThuMonthonly, currentMonth, renderDoanhThuGanDay, renderDoctorChart} = moduleRender.default
        renderDoanhThuGanDay(dataRecently)
        renderDoctorChart(dataDoctor)
        renderDoanhThuMonthonly(dataMonthlonly)


        const tbody = document.getElementById('table-body');

        const totalRevenue = dataDoctor.data.reduce((sum, item) => sum + item.doanh_thu, 0);

        let html = '';
        dataDoctor.data.forEach(bs => {
            let phanTram = totalRevenue > 0 ? (bs.doanh_thu / totalRevenue * 100).toFixed(1) : 0;
            const formatMoney = (amount) => {
                return new Intl.NumberFormat('vi-VN', {style: 'currency', currency: 'VND'}).format(amount);
            };
            html += `
                        <tr>
                            <td>${bs.ho_ten_bac_si}</td>
                            <td>${bs.so_luot_kham}</td>
                            <td>${formatMoney(bs.doanh_thu)}</td>
                            <td>${formatMoney(bs.trung_binh_doanh_thu)}</td>
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