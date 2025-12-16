function goToReceptionist(btn) {
    const url = btn.dataset.url;
    if (url) {
        window.location.href = url;
    }
}
