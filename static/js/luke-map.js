const mapElement = document.getElementById("map");

if (mapElement) {
    const lat = Number.parseFloat(mapElement.dataset.lat);
    const lng = Number.parseFloat(mapElement.dataset.lng);

    if (Number.isFinite(lat) && Number.isFinite(lng)) {
        const map = L.map("map").setView([lat, lng], 5);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
        }).addTo(map);

        const marker = L.marker([lat, lng]).addTo(map);
        marker.bindPopup(`<b>IP Location</b><br>Lat: ${lat}<br>Lng: ${lng}`).openPopup();
    }
}
