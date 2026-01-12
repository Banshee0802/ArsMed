document.addEventListener('DOMContentLoaded', function () {
    const link = document.getElementById('requests-link');
    const badge = document.getElementById('requests-badge');
    if (!link || !badge) return;

    const apiUrl = link.dataset.apiUrl; 

    async function updateBadge() {
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) return;

            const data = await response.json();
            if (data.count > 0) {
                badge.style.display = 'inline-block';
                badge.textContent = data.count;
            } else {
                badge.style.display = 'none';
            }
        } catch (error) {
            console.error('Error fetching badge count:', error);
        }
    }

    updateBadge();               
    setInterval(updateBadge, 10000); 
});

