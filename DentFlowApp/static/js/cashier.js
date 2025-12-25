document.addEventListener("DOMContentLoaded", function () {
    const BANK_CONFIG = window.BANK_ENV_CONFIG;
    const dsBtn = document.querySelectorAll('.btn-pt');
    const hiddenInput = document.getElementById('paymentMethodInput');
    const qrArea = document.getElementById('qrCodeArea');
    const qrImage = document.getElementById('qrImage');
    const tongTienElem = document.getElementById('tong-tien');

    const checkbox = document.getElementById('confirmPayment');
    const btnSubmit = document.getElementById('btnSubmit');

    if (checkbox && btnSubmit) {
        checkbox.addEventListener('change', function () {
            btnSubmit.disabled = !this.checked;
        });
    }

    if (dsBtn.length > 0) {
        dsBtn.forEach(btn => {
            btn.addEventListener('click', function () {
                dsBtn.forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                const method = this.getAttribute('data-value');

                if (hiddenInput) hiddenInput.value = method;

                handleQRCode(method);
            });
        });
    }

    function handleQRCode(method) {
        if (!qrArea || !qrImage) return;
        if (method === '1') {
            qrArea.classList.add('d-none');
        } else {
            let rawPrice = tongTienElem ? tongTienElem.innerText : "0";
            let amount = rawPrice.replace(/[^0-9]/g, '');

            qrArea.classList.remove('d-none');

            if (method === '2') {
                let content = "Thanh toan vien phi";
                let url = `https://img.vietqr.io/image/${BANK_CONFIG.BANK_ID}-${BANK_CONFIG.ACCOUNT_NO}-${BANK_CONFIG.TEMPLATE}.png?amount=${amount}&addInfo=${content}`;
                qrImage.src = url;
            } else if (method === '3') {
                qrImage.src = "/static/images/momo.png";
            }
        }
    }
});