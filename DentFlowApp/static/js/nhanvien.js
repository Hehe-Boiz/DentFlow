async function loadEmployees() {
    try {
        const response = await fetch('/manager/nhan-vien');
        const result = await response.json();

        const container = document.getElementById('employee-list');
        if (container.id === 'nhan-vien') {
            container.innerHTML = '';

            if (result.status === 'success' && result.data.length > 0) {
                result.data.forEach(nv => {

                    const initials = nv.ho_ten.split(' ').pop().charAt(0).toUpperCase();

                    const cardHtml = `
                        <div class="col-12 col-md-6 col-lg-4 col-xl-3">
                            <div class="card rounded-xl card-hover">
                                <div class="card-header bg-primary text-white">
                                    <h5 class="card-title mb-0 text-truncate" title="${nv.ho_ten}">${nv.ho_ten}</h5>
                                    <small class="opacity-75">ID: ${nv.ma_nhan_vien}</small>
                                </div>
                              
    
                                <div class="card-body">
                                    <div class="info-item">
                                        <i class="fas fa-phone-alt"></i>
                                        <span>${nv.so_dien_thoai || 'Chưa cập nhật'}</span>
                                    </div>
                                    <div class="info-item">
                                        <i class="fas fa-birthday-cake"></i>
                                        <span>Năm sinh: ${nv.nam_sinh}</span>
                                    </div>
                                    <div class="info-item">
                                        <i class="fas fa-calendar-check"></i>
                                        <span>Vào làm: ${nv.ngay_vao_lam}</span>
                                    </div>
                                    
                                    
                                   
                                </div>
                            </div>
                        </div>
                    `;
                    container.insertAdjacentHTML('beforeend', cardHtml);
                });
            } else {
                container.innerHTML = '<div class="alert alert-warning">Không có dữ liệu nhân viên.</div>';
            }
        }
    } catch
        (error) {
        console.error('Lỗi:', error);
        document.getElementById('employee-list').innerHTML =
            '<div class="alert alert-danger">Lỗi khi tải dữ liệu nhân viên.</div>';
    }

}

document.addEventListener('load', async function () {
    await loadEmployees();
});
