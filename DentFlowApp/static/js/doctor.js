import {initCreateTreatment} from './create_treatment.js';


const tabApiMap = {
    "tab-treatment": "/tabs/treatment",
    "tab-today": "/tabs/today",
    "tab-work": "/tabs/work"
};
let buttons = document.querySelectorAll('.tab-btn');


buttons.forEach(btn => {
    btn.addEventListener('click', async () => {
        const target = btn.dataset.tab;
        const url = tabApiMap[target];

        if (!url) return;
        buttons.forEach(b => {
            b.classList.remove('bg-blue-600', 'text-white', 'shadow-md');
            b.classList.add('text-gray-600', 'hover:bg-gray-100');
        });
        btn.classList.remove('text-gray-600', 'hover:bg-gray-100');
        btn.classList.add('bg-blue-600', 'text-white', 'shadow-md');

        const tabel = document.getElementById("tab-content-container");
        if (!tabel) return;

        tabel.style.opacity = "0.5";
        tabel.style.pointerEvents = "none";

        try {
            let res = await fetch(url);
            if (!res.ok) throw new Error('Network response was not ok');
            let html = await res.text();
            tabel.innerHTML = html;

            if (target === 'tab-treatment') {
                initCreateTreatment();
            }
            if (target === 'tab-work') {
                initCalendarWork();
            }
            if (target === 'tab-today') {
                const buttons = document.querySelectorAll(".btn-phieu-dieu-tri");
                buttons.forEach(btn => {
                    btn.addEventListener("click", async () => {
                        const patientId = btn.dataset.patientId;
                        const dichVu = btn.dataset.dichvu;

                        const url = `/tabs/treatment?patient_id=${patientId}&dichvu=${dichVu}`;
                        res = await fetch(url);
                        html = await res.text();
                        tabel.innerHTML = html;
                        const listContainer = document.getElementById('service-list-container');
                        listContainer.classList.remove('hidden');
                        initCreateTreatment()

                    });
                });
                initToday();
            }

        } catch (error) {
            console.error("Lỗi tải tab:", error);
            tabel.innerHTML = `<p class="text-red-500 p-4">Không thể tải dữ liệu. Vui lòng thử lại.</p>`;
        } finally {
            tabel.style.opacity = "1";
            tabel.style.pointerEvents = "auto";
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    let currentTabId = params.get('tab');

    if (!currentTabId) {
        currentTabId = 'tab-today';
    }

    const targetBtn = document.querySelector(`.tab-btn[data-tab="${currentTabId}"]`);

    if (targetBtn) {
        targetBtn.click();
    }
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

function initToday() {
    const badges = document.querySelectorAll(".trang-thai-lich-hen");

    badges.forEach(span => {
        const statusKey = span.getAttribute("data-trang-thai").trim();
        console.log(statusKey)
        const config = STATUS_MAP[statusKey];

        if (config) {
            span.innerHTML = ""
            span.classList.remove(
                "bg-green-100", "text-green-700",
                "bg-yellow-100", "text-yellow-700",
            );
            span.classList.add(...config.classes);

            span.innerHTML = `<i class="${config.icon}"></i>${config.text}`;
        }
    });
}

function initCalendarWork() {
    const navElement = document.getElementById('schedule-nav');
    if (navElement) {
        const btnPrev = document.getElementById('btn-prev-week');
        const btnNext = document.getElementById('btn-next-week');
        const btnToday = document.getElementById('btn-this-week');

        if (btnPrev) btnPrev.addEventListener('click', () => changeWeek(-1));
        if (btnNext) btnNext.addEventListener('click', () => changeWeek(1));
        if (btnToday) btnToday.addEventListener('click', () => goToThisWeek());
    }

    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    async function loadWorkTab(url) {
        const container = document.getElementById("tab-content-container");
        container.style.opacity = "0.5";
        try {
            const res = await fetch(url);
            const html = await res.text();
            container.innerHTML = html;
            initCalendarWork();
        } catch (error) {
            console.error("lỗi:", error);
        } finally {
            container.style.opacity = "1";
        }
    }

    function changeWeek(offset) {
        const currentMondayStr = navElement.getAttribute('data-monday');
        const currentMonday = new Date(currentMondayStr);
        currentMonday.setDate(currentMonday.getDate() + (offset * 7));

        const newDateStr = formatDate(currentMonday);
        // Tải tuần mới qua AJAX
        loadWorkTab(`/tabs/work?day=${newDateStr}`);
    }

    function goToThisWeek() {
        loadWorkTab(`/tabs/work`);
    }

// hiện ô nhỏ
    const popup = document.getElementById("slot-popup");
    const popupTitle = document.getElementById("popup-title");
    const popupSubtitle = document.getElementById("popup-subtitle");
    const popupTotal = document.getElementById("popup-total");
    const popupContent = document.getElementById("popup-content");
    const popupClose = document.getElementById("popup-close");

    function hidePopup() {
        popup.classList.add("hidden");
        popupContent.innerHTML = "";
    }

    function clamp(n, min, max) {
        return Math.max(min, Math.min(max, n));
    }

    function positionPopupNear(el) {
        const r = el.getBoundingClientRect();

        let left = r.right + 8;
        let top = r.top;

        const margin = 8;
        const popupWidth = popup.offsetWidth || 384;
        const popupHeight = popup.offsetHeight || 300;

        left = clamp(left, margin, window.innerWidth - popupWidth - margin);
        top = clamp(top, margin, window.innerHeight - popupHeight - margin);

        popup.style.left = `${left}px`;
        popup.style.top = `${top}px`;
    }

    function renderNoAppointments() {
        popupTotal.textContent = "0 lịch hẹn";
        popupContent.innerHTML = `
      <div class="p-3 rounded-lg bg-gray-50 border border-gray-200 text-sm text-gray-500">
        Không có cuộc hẹn
      </div>
    `;
    }

    function renderAppointments(items) {
        popupTotal.textContent = `${items.length} lịch hẹn`;

        popupContent.innerHTML = items.map((x, idx) => {
            // status badge
            const statusText = x.trang_thai_text || "Chờ khám";
            const statusClass = (statusText.includes("Chờ"))
                ? "bg-amber-600 text-white"
                : (statusText.includes("Đã") ? "bg-green-600 text-white" : "bg-gray-600 text-white");

            return `
        <div class="border rounded-lg p-3 bg-amber-50 border-amber-300">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center space-x-2">
              <span class="text-xs font-medium text-gray-900">#${idx + 1}</span>
              <span class="text-[10px] px-2 py-0.5 rounded ${statusClass}">${statusText}</span>
            </div>
            <span class="text-xs font-semibold text-gray-900">${x.gio_kham}</span>
          </div>

          <div class="space-y-1.5 text-xs">
            <div class="flex items-start">
                <i class="fa-regular fa-user fa-sm w-3.5 h-3.5 text-gray-500 mr-2 mt-2 flex-shrink-0"></i>
                <div class="min-w-0 flex-1"><p class="text-gray-500 text-[10px] mb-0">Bệnh nhân</p>
                            <p class="text-gray-900 font-medium truncate mb-0">${x.benh_nhan_ho_ten}</p></div>
            </div>
            
            <div class="flex items-start">
            <i class="fa-solid fa-book-open w-3.5 h-3.5 text-gray-500 mr-2 mt-2 flex-shrink-0 fa-sm"></i>
                <div class="min-w-0 flex-1"><p class="text-gray-500 text-[10px] mb-0">Dịch vụ</p>
                            <p class="text-gray-900 truncate mb-0">${x.dich_vu_ten || "—"}</p></div>
            </div>
          </div>

          <div class="mt-2 pt-2 border-t border-gray-200">
            <p class="text-gray-500 text-[10px] mb-1">Ghi chú</p>
            <p class="text-gray-700 text-xs mb-0">${x.ghi_chu || "—"}</p>
          </div>
        </div>
      `;
        }).join("");
    }

    async function fetchAppointments(dateStr, timeStr) {
        const url = `/treatment/lich-hen/slot?date=${encodeURIComponent(dateStr)}&time=${encodeURIComponent(timeStr)}`;

        const res = await fetch(url, {headers: {"Accept": "application/json"}});
        if (!res.ok) throw new Error("thất bại");
        return await res.json();
    }

    document.addEventListener("click", (e) => {
        if (popup.classList.contains("hidden")) return;
        const clickedInside = popup.contains(e.target);
        const clickedCell = e.target.closest(".slot-cell");
        if (!clickedInside && !clickedCell) hidePopup();
    });

    popupClose.addEventListener("click", hidePopup);
    window.addEventListener("scroll", () => {
        if (!popup.classList.contains("hidden")) hidePopup();
    });
    window.addEventListener("resize", () => {
        if (!popup.classList.contains("hidden")) hidePopup();
    });

    document.querySelectorAll(".slot-cell").forEach(cell => {
        cell.addEventListener("click", async (e) => {
            e.stopPropagation();

            const dateStr = cell.dataset.date;
            const timeStr = cell.dataset.time;

            popup.classList.remove("hidden");
            popupTitle.textContent = "Lịch hẹn";
            popupSubtitle.textContent = `${dateStr} • ${timeStr}`;
            popupTotal.textContent = "Đang tải...";
            popupContent.innerHTML = `
        <div class="p-3 rounded-lg bg-blue-50 border border-blue-100 text-sm text-blue-700">
          Đang tải lịch hẹn...
        </div>
      `;

            positionPopupNear(cell);

            try {
                const data = await fetchAppointments(dateStr, timeStr);

                if (!data || data.status !== "success") {
                    renderNoAppointments();
                    return;
                }
                const items = data.items || [];
                if (items.length === 0) renderNoAppointments();
                else renderAppointments(items);

                positionPopupNear(cell);

            } catch (err) {
                popupTotal.textContent = "0 lịch hẹn";
                popupContent.innerHTML = `
          <div class="p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">
            lỗi 
          </div>
        `;
                positionPopupNear(cell);
            }
        });
    });
}