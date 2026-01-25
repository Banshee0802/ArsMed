document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toggle-doctor').forEach(title => {
    const id = title.dataset.doctorId;
    const content = document.getElementById(`doctor-${id}`);
    if (!content) return;

    const arrow = document.createElement('span');
    arrow.textContent = ' ▼';
    arrow.style.marginLeft = '8px';
    title.appendChild(arrow);

    title.addEventListener('click', () => {
      content.classList.toggle('hidden');
      arrow.textContent = content.classList.contains('hidden') ? ' ▼' : ' ▲';
    });
  });
});