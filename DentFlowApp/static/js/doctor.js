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

        const res = await fetch(url, { cache: "no-store" });
        tabEl.innerHTML = await res.text();
    });
});