document.addEventListener('DOMContentLoaded', function () {
    const titles = document.querySelectorAll('.toggle-doctor');

    titles.forEach(title => {
        const doctorId = title.dataset.doctorId;
        const block = document.getElementById(`doctor-${doctorId}`);

        const arrow = document.createElement('span');
        arrow.textContent = "▼";
        arrow.style.marginLeft = "10px";
        title.appendChild(arrow);

        title.addEventListener('click', () => {
            if (!block) return;
            block.classList.toggle('hidden');

            arrow.textContent = block.classList.contains('hidden') ? "▼" : "▲";
        });
    });
});
