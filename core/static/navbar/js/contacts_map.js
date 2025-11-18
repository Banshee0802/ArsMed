document.addEventListener("DOMContentLoaded", function () {
    if (typeof ymaps === "undefined") return;

    ymaps.ready(function () {
        document.querySelectorAll(".map").forEach(function (mapEl) {
            const lat = parseFloat(mapEl.dataset.lat);
            const lon = parseFloat(mapEl.dataset.lon);
            const title = mapEl.dataset.title;

            if (!lat || !lon) return;

            const map = new ymaps.Map(mapEl.id, {
                center: [lat, lon],
                zoom: 14
            });

            const placemark = new ymaps.Placemark([lat, lon], {
                balloonContent: title
            });

            map.geoObjects.add(placemark);
        });
    });
});
