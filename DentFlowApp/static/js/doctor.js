const tabApiMap = {
    "tab-treatment": "/tabs/treatment",
    "tab-today": "/tabs/today",
    "tab-work": "/tabs/work"
};
const buttons = document.querySelectorAll('.tab-btn');
const contentTab = document.getElementById('content-tab')

buttons.forEach(btn => {
    btn.addEventListener('click', () => {
        const target = btn.dataset.tab;


    });
});

buttons.forEach(btn => {
    btn.addEventListener('click', async () => {
        const target = btn.dataset.tab;
        const url = tabApiMap[target];

        if (!url) return;

        const tabEl = document.getElementById(target);

        document.querySelectorAll(".tab-content")
            .forEach(t => t.classList.add("hidden"));
        tabEl.classList.remove("hidden");

        tabEl.innerHTML = "<p class='text-sm text-gray-500'>Đang tải...</p>";

        const res = await fetch(url, {cache: "no-store"});
        tabEl.innerHTML = await res.text();
    });
});

const STATUS_MAP = {
    "Đã khám": {
        text: "Đã khám",
        classes: ["bg-green-100", "text-green-700"],
        icon: "fa-regular fa-circle-check fa-lg mt-2-5 w-3 h-3 mr-2"
    },
    "Chờ khám": {
        text: "Chờ khám",
        classes: ["bg-yellow-100", "text-yellow-700"],
        icon: "fa-regular fa-clock fa-lg mt-2-5 w-3 h-3 mr-2"
    },
};


const badges = document.querySelectorAll(".trang-thai-lich-hen");

badges.forEach(span => {
    // Lấy giá trị từ data-trang-thai (được render từ Jinja2)
    const statusKey = span.getAttribute("data-trang-thai");
    console.log(statusKey)
    // Tìm cấu hình trong Map
    const config = STATUS_MAP[statusKey];

    if (config) {
        span.innerHTML =""
        // Xóa các class màu mặc định (để tránh bị trùng lặp)
        span.classList.remove(
                "bg-green-100", "text-green-700",
                "bg-yellow-100", "text-yellow-700",
            );
        span.classList.add(...config.classes);

        span.innerHTML = `<i class="${config.icon}"></i>${config.text}`;
    }
});
