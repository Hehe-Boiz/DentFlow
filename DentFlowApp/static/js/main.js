function goToReceptionist(btn) {
    const url = btn.dataset.url;
    if (url) {
        window.location.href = url;
    }
}

function getDataProfile(so_dien_thoai, ho_ten, user_id) {
    let ht = document.getElementById('input_ho_ten')
    let sdt = document.getElementById('input_so_dien_thoai')
    let u_id = document.getElementById('input_user_id')
    ht.value = ho_ten
    sdt.value = so_dien_thoai
    u_id.value = user_id
    ht.readOnly = true;
    sdt.readOnly = true;
    ht.style.backgroundColor = "#e9ecef";
    sdt.style.backgroundColor = "#e9ecef";
}