document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('id_phone');
    if (phoneInput) {
        IMask(phoneInput, {
            mask: '+{7} (000) 000-00-00'
        });
    }
});