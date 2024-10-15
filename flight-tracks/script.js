
let fnames = [
	'Flight%20Track%20Log%20%E2%9C%88%20N3927%2005-Feb-2024%20%28PHNL-PHNL%29%20-%20FlightAware.webarchive',
	'Flight%20Track%20Log%20%E2%9C%88%20N3927%2001-Mar-2024%20%28PHNL-PHNL%29%20-%20FlightAware.webarchive',
	'Flight%20Track%20Log%20%E2%9C%88%20N3927%2004-Mar-2024%20%28PHIK-PHNL%29%20-%20FlightAware.webarchive',
	'Flight%20Track%20Log%20%E2%9C%88%20N3927%2020-Mar-2024%20%28PHNL-PHNL%29%20-%20FlightAware.webarchive',
	'Flight%20Track%20Log%20%E2%9C%88%20N3927%2022-Jun-2024%20%28PHNL-PHNL%29%20-%20FlightAware.webarchive',
	'Flight%20Track%20Log%20%E2%9C%88%20N65584%2023-Sep-2024%20%28KBJC-KBJC%29%20-%20FlightAware.webarchive',
];

async function loadData(fnames) {
	let data = [];
	for (fname of fnames) {
		let response = await fetch('./data/' + fname);
		let file = await response.text();
		data.push(file);
	}
	return data;
}

async function processData() {
	let data = await loadData(fnames);
	let output = [];
	for (str of data) {
		let flight = [];
		let table_indices = Array.from(str.matchAll(/<tr class="smallrow[1,2]"/g), (m) => m.index);
		let tables = Array.from(table_indices, (m) => str.slice(m, str.indexOf('</tr>', m)));
		let values = Array.from(tables, (t) => {
			let value_indices = Array.from(t.matchAll(/<span/g), (m) => m.index);
			return Array.from(value_indices, (v) => t.slice(t.indexOf('>', v)+1, t.indexOf('</span>', v)));
		});
		Array.from(values, (v) => {
			// [time, lat, lon, heading]
			flight.push([v[1], v[2], v[4], v[6]]);
		});
		output.push(flight);
	}
	return output;
}

async function createTracks() {
	let output = await processData();
	let tracks = [];
	for (flight of output) {
		let points = Array.from(flight, (f) => {
			return [f[2], f[1]];
		});
		tracks.push(points);
	}
	return tracks;
}

async function plotTrack(idx) {
	let tracks = await createTracks();
	let track = tracks[4];
	let line = {type: 'LineString', coordinates: track};
	let [clon, clat] = d3.geoCentroid(line);
	let buffer = 0.55
	const projection = d3.geoOrthographic();
	const canvas = document.getElementById('canvas');
	const context = canvas.getContext('2d');
	const path = d3.geoPath(projection, context);
	let land_path = './maps/ne_10m_land.json';  // geojson
	let land_data;
	await d3.json(land_path)
	.then(function(data) {
		land_data = data;
	});
	let coastline_path = './maps/ne_10m_coastline.json';  // geojson
	let coastline_data;
	await d3.json(coastline_path)
	.then(function(data) {
		coastline_data = data;
	});
	let graticule = d3.geoGraticule();
	async function drawMap() {
		canvas.width = window.innerWidth;
		canvas.height = window.innerHeight;
		projection.rotate([-clon, -clat]);
		projection.fitSize([canvas.width / (1 + buffer), canvas.height / (1 + buffer)], line)
		projection.translate([canvas.width / 2, canvas.height / 2]);
		context.clearRect(0, 0, canvas.width, canvas.height);
		context.beginPath(), path(land_data), context.fillStyle = '#cfe6ad', context.fill();
		context.beginPath(), path(coastline_data), context.strokeStyle = 'white', context.stroke();
		context.beginPath(), path(line), context.strokeStyle = 'black', context.lineWidth = 2, context.stroke();
	}
	drawMap();
	window.addEventListener('resize', function (event) {
		drawMap();
	});
}

plotTrack();
