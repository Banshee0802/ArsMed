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



$(document).ready(function() {
    $('#search-btn').click(function() {
        let q = $('#patient-query').val().trim();
        if (q.length < 2) return;

        $.ajax({
            url: $('script[src*="admin_schedule_toggle.js"]').data('searchUrl'),
            data: { q: q },
            dataType: 'json',
            success: function(data) {
                let html = '';
                if (data.results.length === 0) {
                    html = '<p>Никто не найден</p>';
                } else {
                    data.results.forEach(function(item) {
                      let parts = item.text.split(' | ');
                      let fio = parts[0]?.trim().toUpperCase() || '';
                      let phone = parts[1]?.trim() || '-';
                      let birth = parts[2]?.trim() || '-';

                      html += `<div class="patient-item" data-id="${item.id}" data-text="${item.text}">
                      <strong>${fio}</strong><br>
                      Телефон: ${phone}<br>
                      Дата рождения: ${birth}
                    </div>`;
                    });
                }
                $('#patient-results').html(html);
            }
        });
    });

    $(document).on('click', '.patient-item', function() {
        let id = $(this).data('id');
        let originalText = $(this).data('text');
        let parts = originalText.split(' | ');
        let fio = (parts[0] || '').trim().toUpperCase();
        let phone = (parts[1] || '-').trim();
        let birth = (parts[2] || '-').trim();

         $('#selected-patient').html(
            `Выбран:<br>` +
            `<strong>${fio}</strong><br>` +
            `Телефон: ${phone}<br>` +
            `Дата рождения: ${birth}`
          );

          $('#selected-patient-id').val(id);

          // Очистка результатов поиска
          $('#patient-results').html('');

          $('#patient-query').val('');
    });
});