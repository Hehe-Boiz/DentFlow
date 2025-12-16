function selectService(element, id) {
    // 1. Xóa class 'selected' ở tất cả các item
    const allItems = document.querySelectorAll('.service-item');
    allItems.forEach(item => item.classList.remove('selected'));

    // 2. Thêm class 'selected' vào item vừa bấm
    element.classList.add('selected');

    // 3. Gán giá trị ID vào input ẩn (để gửi về server Flask)
    document.getElementById('selectedServiceId').value = id;

    // 4. Kích hoạt nút Tiếp tục
    document.getElementById('btnContinue').disabled = false;
}