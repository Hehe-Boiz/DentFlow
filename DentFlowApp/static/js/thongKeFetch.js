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

async function fetchDoanhThuGanDay() {
    const result = await request('/manager/statistics/daily-recently');
    return result ? result.data : null
}

async function fetchDoanhThuMonthlyOnly(month = null) {
    const queryParam = month ? `?month=${month}` : '';
    const result = await request(`/manage/statistics/monthly-only${queryParam}`);
    return result || null
}


async function fetchDoctorOnly(ma_bac_si = null) {
    const queryParam = ma_bac_si ? `?doctor=${ma_bac_si}` : '';
    const result = await request(`/manage/statistics/doctors-only${queryParam}`);
    return result || null
}


export default {
    fetchDoanhThuGanDay,
    fetchDoctorOnly,
    fetchDoanhThuMonthlyOnly
}