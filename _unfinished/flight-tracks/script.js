
// https://geotiffjs.github.io/geotiff.js/
// https://yangdanny97.github.io/blog/2020/11/26/D3-elevations
async function loadMap(w, h, clon, clat, bounds) {
	//const tiff = await d3.buffer('./maps/HYP_HR_SR_OB_DR/HYP_HR_SR_OB_DR.tif')
	const tiff = await d3.buffer('./maps/GMTED2010N30W120_075/30n120w_20101117_gmted_mea075.tif')
	.then(buffer => GeoTIFF.fromArrayBuffer(buffer));
	const image = await tiff.getImage();
	const image_w = image.getWidth(), image_h = image.getHeight();
	let ix = Math.floor(((image_w / 360) * 180) + ((image_w / 360) * clon));
	let iy = Math.floor(((image_h / 180) * 90) - ((image_h / 180) * clat));
	let sx = Math.floor((image_w / 360) * Math.abs(parseFloat(bounds[0][0]) - parseFloat(bounds[1][0])));
	let sy = Math.floor((image_h / 180) * Math.abs(parseFloat(bounds[0][1]) - parseFloat(bounds[1][1])));
	console.log(ix, iy, sx, sy)
	//const data = await image.readRGB({ window: [ix, iy, ix+sx, iy+sy], interleave: false });
	const data = await image.readRasters({ bbox: [-110, 35, -100, 40], resX: 0.1, resY: 0.1 });
	console.log(image.getBoundingBox())
	console.log(data)
	const canvas = document.getElementById('canvas');
	const context = canvas.getContext('2d');
	// https://stackoverflow.com/questions/13826319/copy-a-2-dimensional-pixel-array-to-a-javascript-canvas
	var imgData = context.getImageData(0, 0, w, h);
	var data_tmp = imgData.data;  // the array of RGBA values
	for(var i = 0; i < h; i++) {
		for(var j = 0; j < w; j++) {
			var s = 4 * i * w + 4 * j;  // calculate the index in the array
			data_tmp[s] = data[0][s];
			data_tmp[s + 1] = data[0][s];
			data_tmp[s + 2] = data[0][s];
			data_tmp[s + 3] = 255;
			//data_tmp[s + 1] = data[1][s];
			//data_tmp[s + 2] = data[2][s];
			//data_tmp[s + 3] = 255;  // fully opaque
		}
	}
	context.putImageData(imgData, 0, 0);
}

let fnames = [
	'Flight Track Log ✈ N3517S 03-May-2025 (KBJC-KBJC) - FlightAware.webarchive',
	'Flight Track Log ✈ N5178S 08-May-2025 (KBJC-KBJC) - FlightAware.webarchive',
	'Flight Track Log ✈ N5178S 10-May-2025 (KBJC-KFMM) - FlightAware.webarchive',
	'Flight Track Log ✈ N5178S 10-May-2025 (KFMM-KBJC) - FlightAware.webarchive',
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

async function plotTracks() {
	let tracks = await createTracks();
	let tracks_merged = [].concat.apply([], tracks);
	let tracks_merged_line = {type: 'LineString', coordinates: tracks_merged};
	let buffer = 0
	const projection = d3.geoOrthographic();
	const canvas = document.getElementById('canvas');
	const context = canvas.getContext('2d');
	const path = d3.geoPath(projection, context);
	let [clon, clat] = d3.geoCentroid(tracks_merged_line);
	let bounds = d3.geoBounds(tracks_merged_line);
	console.log(bounds)
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
		projection.fitSize([canvas.width / (1 + buffer), canvas.height / (1 + buffer)], tracks_merged_line);
		//projection.translate([canvas.width / 2, canvas.height / 2]);
		context.clearRect(0, 0, canvas.width, canvas.height);
		//context.beginPath(), path(land_data), context.fillStyle = '#cfe6ad', context.fill();
		//context.beginPath(), path(coastline_data), context.strokeStyle = 'white', context.stroke();
		for (let track of tracks) {
			let line = {type: 'LineString', coordinates: track};
			context.beginPath(), path(line), context.strokeStyle = 'black', context.lineWidth = 2, context.stroke();
		}
		loadMap(canvas.width * 4, canvas.height * 4, clon, clat, bounds);
	}
	loadMap(canvas.width * 4, canvas.height * 4, clon, clat, bounds);
	//drawMap();
	window.addEventListener('resize', function (event) {
		drawMap();
	});
}

plotTracks();
