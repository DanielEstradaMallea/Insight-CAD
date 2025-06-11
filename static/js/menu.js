function setDarkToggleBtn(btn, isDark) {
    if (!btn) return;
    btn.classList.toggle('sun', !isDark);
    btn.classList.toggle('moon', isDark);
    // No tocar la clase del ícono
}

function toggleDarkMode() {
    const isDark = !document.body.classList.contains('dark-mode');
    document.body.classList.toggle('dark-mode');
    setDarkToggleBtn(document.getElementById('toggleDark'), isDark);
    setDarkToggleBtn(document.getElementById('toggleDarkMobile'), isDark);
    localStorage.setItem('dark-mode', isDark);
}

document.getElementById('toggleDark')?.addEventListener('click', toggleDarkMode);
document.getElementById('toggleDarkMobile')?.addEventListener('click', toggleDarkMode);

(function () {
    const isDark = localStorage.getItem('dark-mode') === 'true';
    if (isDark) document.body.classList.add('dark-mode');
    setDarkToggleBtn(document.getElementById('toggleDark'), isDark);
    setDarkToggleBtn(document.getElementById('toggleDarkMobile'), isDark);
})();



document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.querySelector('.menu-toggle');
    const offcanvas = document.getElementById('offcanvasSidebar');
    if (toggleBtn && offcanvas) {
        offcanvas.addEventListener('show.bs.offcanvas', function () {
            toggleBtn.style.display = 'none';
        });
        offcanvas.addEventListener('hidden.bs.offcanvas', function () {
            toggleBtn.style.display = '';
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.querySelector('.menu-toggle');
    const offcanvas = document.getElementById('offcanvasSidebar');
    if (toggleBtn && offcanvas) {
        offcanvas.addEventListener('show.bs.offcanvas', function () {
            toggleBtn.style.display = 'none';
        });
        offcanvas.addEventListener('hidden.bs.offcanvas', function () {
            toggleBtn.style.display = '';
        });
    }
});

