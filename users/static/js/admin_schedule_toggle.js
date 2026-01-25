document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toggle-doctor').forEach(title => {
    const id = title.dataset.doctorId;
    const content = document.getElementById(`doctor-${id}`);
    if (!content) return;

    const arrow = document.createElement('span');
    arrow.textContent = ' ▼';
    arrow.style.marginLeft = '8px';
    title.appendChild(arrow);

    const isOpen = localStorage.getItem(`doctor-${id}-open`) === 'true';
    if (isOpen) {
      content.classList.remove('hidden');
      arrow.textContent = ' ▲';
    }

    title.addEventListener('click', () => {
      content.classList.toggle('hidden');
      const isHidden = content.classList.contains('hidden');
      arrow.textContent = isHidden ? ' ▼' : ' ▲';
      localStorage.setItem(`doctor-${id}-open`, !isHidden);
    });
  });
});