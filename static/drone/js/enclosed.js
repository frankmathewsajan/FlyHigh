// Initialize map at VIT AP Campus
const vitApLat = 16.4819, vitApLng = 80.5083;
const map = L.map('map').setView([vitApLat, vitApLng], 16); // Zoom level 16 for campus view
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Initialize layers and global variables
let coordinates = [];
const markers = [];
let mstLayer = L.layerGroup().addTo(map);

// Function to calculate distances between points (Haversine formula)
const calculateDistance = (p1, p2) => {
    const R = 6371e3; // Earth's radius in meters
    const toRad = deg => (deg * Math.PI) / 180;

    const lat1 = toRad(p1[0]), lon1 = toRad(p1[1]);
    const lat2 = toRad(p2[0]), lon2 = toRad(p2[1]);

    const dlat = lat2 - lat1;
    const dlon = lon2 - lon1;

    const a = Math.sin(dlat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dlon / 2) ** 2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Distance in meters
};

// Add a marker and store coordinates on map click
map.on('click', function (e) {
    const marker = L.marker(e.latlng).addTo(map);

    marker.on('click', function () {
        map.removeLayer(marker); // Remove marker on click
        const index = coordinates.findIndex(coord => coord[0] === e.latlng.lat && coord[1] === e.latlng.lng);
        if (index > -1) coordinates.splice(index, 1); // Remove from coordinates array
        document.getElementById('coordinates').value = JSON.stringify(coordinates);
    });

    markers.push(marker);
    coordinates.push([e.latlng.lat, e.latlng.lng]);
    document.getElementById('coordinates').value = JSON.stringify(coordinates);
});

// Clear all markers
document.getElementById('clear-markers').addEventListener('click', () => {
    markers.forEach(marker => map.removeLayer(marker));
    coordinates = [];
    document.getElementById('coordinates').value = JSON.stringify(coordinates);
});

// Clear paths and layers
document.getElementById('clear-paths').addEventListener('click', () => {
    mstLayer.clearLayers();
});

// Handle form submission to calculate and display enclosed region
document.getElementById('coordinates-form').onsubmit = function (event) {
    event.preventDefault();

    fetch('', {
        method: 'POST',
        headers: { 'X-CSRFToken': '{{ csrf_token }}' },
        body: new FormData(this),
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            mstLayer.clearLayers(); // Clear previous layers

            const enclosedRegion = data.enclosed_region;

            // Draw the enclosed region with dashed lines and thin borders
            L.polygon(enclosedRegion, {
                color: 'blue',
                weight: 1,       // Thin border
                fillColor: 'none', // No solid fill
                dashArray: '5, 5' // Dashed shading
            }).addTo(mstLayer);

            // Add distance labels between consecutive points
            for (let i = 0; i < enclosedRegion.length - 1; i++) {
                const p1 = enclosedRegion[i];
                const p2 = enclosedRegion[i + 1];

                const distance = calculateDistance(p1, p2); // Calculate distance
                const midpoint = [
                    (p1[0] + p2[0]) / 2,
                    (p1[1] + p2[1]) / 2
                ];

                // Add distance label at midpoint
                L.marker(midpoint, {
                    icon: L.divIcon({
                        className: 'distance-label',
                        html: `<div style="background: rgba(255, 255, 255, 0.8); padding: 2px; border-radius: 4px; font-size: 10px;">${distance.toFixed(2)} m</div>`,
                        iconSize: [40, 20]
                    })
                }).addTo(mstLayer);
            }
        });
};