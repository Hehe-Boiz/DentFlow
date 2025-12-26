async function request(url) {
    try {
        const respone = await fetch(url);
        const result = await respone.json();
        if (result.status !== 'success') {
            console.error("Lỗi dữ liệu:", result);
        } else {
            console.log('fetch done', result)
            return result
        }
    } catch (e) {
        console.error(`Lỗi request ${url}: `, e)
    }
}

async function fetchMonthly() {
    const result = await request('/manager/statistics/monthly');
    return result ? result.data : null
}

async function fetchDoctors(month) {
    const result = await request(`/manager/statistics/doctors?month=${month}`);
    return result ? result : null
}

async function fetchDoanhThuTrongNamNgay() {
    const result = await request('/manager/statistics/daily-recently');
    return result ? result.data : null
}

async function fetchCTHD(month) {
    const result = await request(`/manager/statistics/monthly?month=${month}`);
    return result ? result.data_ds_hoadon : null
}

async function fetchDoanhThuTheoThang(month) {
    const result = await request(`/manager/statistics/monthly?month=${month}`);
    return result ? result.data : null
}

export default {fetchMonthly, fetchDoctors, fetchDoanhThuTheoThang, fetchCTHD, fetchDoanhThuTrongNamNgay}
