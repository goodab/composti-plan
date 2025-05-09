var map = L.map('map').setView([47.7511, -120.7401], 7);  // Center on Washington State

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

const markersData = [
    { lat: 47.6062, lon: -122.3321, address: 'Seattle, WA', waste_type: 'Recycling', expected_amt: 5, deadline: '2025-06-01' },
    { lat: 48.4284, lon: -123.3656, address: 'Victoria, WA', waste_type: 'Landfill', expected_amt: 10, deadline: '2025-07-01' },
    { lat: 46.5205, lon: -117.1958, address: 'Pullman, WA', waste_type: 'Hazardous', expected_amt: 3, deadline: '2025-08-01' },
    { lat: 47.7511, lon: -120.7401, address: 'Yakima, WA', waste_type: 'Organic', expected_amt: 7, deadline: '2025-09-01' },
    { lat: 48.7591, lon: -122.4873, address: 'Anacortes, WA', waste_type: 'Recycling', expected_amt: 4, deadline: '2025-05-10' },
    { lat: 47.9275, lon: -121.9886, address: 'Snoqualmie, WA', waste_type: 'Landfill', expected_amt: 6, deadline: '2025-06-10' },
    { lat: 48.7590, lon: -122.4810, address: 'Bellingham, WA', waste_type: 'Organic', expected_amt: 8, deadline: '2025-05-20' },
    { lat: 47.4112, lon: -120.3140, address: 'Ellensburg, WA', waste_type: 'Hazardous', expected_amt: 2, deadline: '2025-08-20' },
    { lat: 46.9857, lon: -123.9869, address: 'Olympia, WA', waste_type: 'Recycling', expected_amt: 12, deadline: '2025-07-15' },
    { lat: 47.0585, lon: -122.3477, address: 'Tacoma, WA', waste_type: 'Landfill', expected_amt: 9, deadline: '2025-06-30' }
];

markersData.forEach(markerData => {
    const { lat, lon, address, waste_type, expected_amt, deadline } = markerData;
    const marker = L.marker([lat, lon]).addTo(map);
    
    marker.bindPopup(`
        <b>Address:</b> ${address}<br>
        <b>Waste Type:</b> ${waste_type}<br>
        <b>Expected Amount:</b> ${expected_amt} units<br>
        <b>Deadline:</b> ${new Date(deadline).toLocaleString()}
    `);
});
