const slider = document.getElementById('expertsSlider');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const progressFill = document.getElementById('progressFill');
const dots = document.querySelectorAll('.dot');

const cardWidth = 305;
const totalCards = document.querySelectorAll('.expert-card').length;

function updateIndicators() {
    const scrollLeft = slider.scrollLeft;
    const maxScroll = slider.scrollWidth - slider.clientWidth;
    const scrollPercent = scrollLeft / maxScroll;

    const progressWidth = 30;
    const maxLeft = 100 - progressWidth;
    progressFill.style.left = (scrollPercent * maxLeft) + '%';

    const activeIndex = Math.round(scrollLeft / cardWidth);
    dots.forEach((dot, index) => {
        dot.classList.toggle('active', index === activeIndex);
    });
}

slider.addEventListener('scroll', updateIndicators);

prevBtn.addEventListener('click', function () {
    slider.scrollBy({
        left: -cardWidth,
        behavior: 'smooth'
    });
});

nextBtn.addEventListener('click', function () {
    slider.scrollBy({
        left: cardWidth,
        behavior: 'smooth'
    });
});

dots.forEach((dot, index) => {
    dot.addEventListener('click', function () {
        slider.scrollTo({
            left: index * cardWidth,
            behavior: 'smooth'
        });
    });
});

updateIndicators();
document.querySelectorAll('.faq-question').forEach(question => {
    question.addEventListener('click', () => {
        const faqItem = question.parentElement;
        const icon = question.querySelector('.faq-icon');

        // Close all other FAQ items
        document.querySelectorAll('.faq-item').forEach(item => {
            if (item !== faqItem) {
                item.classList.remove('active');
                item.querySelector('.faq-icon').classList.remove('fa-arrow-up');
                item.querySelector('.faq-icon').classList.add('fa-arrow-down');
            }
        });

        // Toggle current FAQ item
        faqItem.classList.toggle('active');
        if (faqItem.classList.contains('active')) {
            icon.classList.remove('fa-arrow-down');
            icon.classList.add('fa-arrow-up');
        } else {
            icon.classList.remove('fa-arrow-up');
            icon.classList.add('fa-arrow-down');
        }
    });
});