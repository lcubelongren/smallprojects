
let wikimedia = {
	headers: {
		'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI4Y2E3MDU0ZjVjN2RhMTFiYjAyZDE5YjM1NzgyYmY4ZSIsImp0aSI6ImUwNDRjNzJmMDU5ZjRmNDc5NzA4Mzc0ODM5NDZjMmViZTQ3NjQzZmIzZDgyY2YwM2YyZDk3NWM5OWQ5NTAxMTU4MmRhM2IxYzE5M2M0OGQ3IiwiaWF0IjoxNzI0MzA5NzI4LjYwOTU2NSwibmJmIjoxNzI0MzA5NzI4LjYwOTU2OCwiZXhwIjozMzI4MTIxODUyOC42MDc0ODcsInN1YiI6IjcxNjU2Mzk2IiwiaXNzIjoiaHR0cHM6Ly9tZXRhLndpa2ltZWRpYS5vcmciLCJyYXRlbGltaXQiOnsicmVxdWVzdHNfcGVyX3VuaXQiOjUwMDAsInVuaXQiOiJIT1VSIn0sInNjb3BlcyI6WyJiYXNpYyJdfQ.G-_ZLwG5R17t6HJMUil8rkZoa20LOc8Caz7vrahxqGvBXFtVW2TH3IXZZqueTjiCP9fgS8vXHVhE43K1hXC7oJasa9HjQxFO4Wi7WHoFMfkyqy-AxhRof_fF6jsp_SqLlyeVGAw4wP-RFfoedXsRRbjDK4zpN9KZDtVNvk-orcCtZlW1EDBmwG-8yKAsgh1i6wVytRH7VS9d2k2dW9svCxeolLDm5t5PmaGZoZWUrCNIT0_08kdXeEi4p2yiRMhiB9xBHrkv4aLBV6CTI5yP-JaprkNDiIw3GOi8m4xfsZp0n9LI8QEO1ClTAJcAnmLO6UbfCD0pXWQ-r3VWjK55fKPAlUMEIH-QtmJq-r-nRKtixPsF6Ifk22mj8aS8ydDrZU-zpfehzxOFdOzmo0LisJNHNHzlBI87TKW2t3Sfx-d1kipeALwDsvVKxDyFVQHfvEj-VmhPmok-sh8us_UA-x8qRf3NQ1maRp6ckG6YTWxkmB-87zM1WdXRlXzdC709I_ABxJlgOHd6-JCv-nHdFRpdz8jy8bZJNZ7G88He5J1LD3qlcwd4AvYv6pI1B_QZAWAeqP8AmJXy-GGWzmLbl6fVV-KmJMSz_RHn-TzxvjmM2ooM9lepJWoaXvtzCSJljEzorn1AwMefmRKBIbYXzzrzjmIVGLDmLw-t2agyTM4',
		'Api-User-Agent': 'Antarctic Stations (lcubelongren@gmail.com)'
	}
}

let url = 'https://api.wikimedia.org/core/v1/wikipedia/en/page/Research_stations_in_Antarctica/html';

async function fetchStationPages() {

	let StationPages = [];
    
	try {
		
		const response = await fetch(url, wikimedia);
		const page = await response.text();
		let parser = new DOMParser();
		let htmlDoc = parser.parseFromString(page, 'text/html');
		
		let tbody = htmlDoc.getElementById('mwpg');
		for (row of tbody.children) {
			let first_column = row.children[0];
			let stations = first_column.getElementsByTagName('a');
			for (station of stations) {
				StationPages.push(station.href);
			}
		}
	return StationPages;

	} catch (error) {
		console.error("Error:", error);
	}
}

async function fetchStationCoordinates() {

	let StationCoordinates = [];

	try {
		
		let StationPages = await fetchStationPages();
	
		for (stationpage of StationPages) {
			let station = stationpage.split('/').slice(-1)[0];
			let station_url = `https://api.wikimedia.org/core/v1/wikipedia/en/page/${station}/html`;
		
			const response = await fetch(station_url, wikimedia);
			const page = await response.text();
			let parser = new DOMParser();
			let htmlDoc = parser.parseFromString(page, 'text/html');
			
			let lon_str = htmlDoc.getElementsByClassName('longitude')[0];
			let lat_str = htmlDoc.getElementsByClassName('latitude')[0];
			if (lon_str && lat_str) {
				let lon_array = lon_str.innerText.split(/[^\d\w]+/);
				let lat_array = lat_str.innerText.split(/[^\d\w]+/);
				let lon = parseFloat(lon_array[0]);  //FIX
				let lat = parseFloat(lat_array[0]);  //FIX
				if (lon_array.slice(-1)[0] == 'W') { lon = lon * -1}
				if (lat_array.slice(-1)[0] == 'S') { lat = lat * -1}
				console.log(station, lon, lat)
				StationCoordinates.push([station, lon, lat]);
			}
		}
	return StationCoordinates;

	} catch (error) {
		console.error("Error:", error);
	}
}

// --------------------------------

async function main() {
	
	let StationCoordinates = await fetchStationCoordinates();

	let geojson_url = 'https://cdn.jsdelivr.net/npm/world-atlas@2/land-50m.json'

	let geojson = {}

	canvas.width = 1200;
	canvas.height = 900;

	let context = d3.select('#canvas')
	.node()
	.getContext('2d');

	let rotation = 0;
	let projection = d3.geoOrthographic()
	.rotate([rotation, 90])
	.scale(canvas.height * 0.99)
	.translate([canvas.width / 2, canvas.height / 2]);

	let geoGenerator = d3.geoPath(projection, context)

	let graticule = d3.geoGraticule();

	let geoStation = d3.geoCircle()
	.radius(0.5);

	let fps = 30;

	function update() {

		context.clearRect(0, 0, canvas.width, canvas.height);
		
		rotation += 5 / fps;
		projection.rotate([rotation, 90]);

		context.beginPath();
		geoGenerator({type: 'FeatureCollection', features: geojson.features})
		context.fillStyle = 'white';
		context.fill();

		context.beginPath();
		geoGenerator(graticule());
		context.strokeStyle = 'white';
		context.lineWidth = 2;
		context.stroke();
		
		context.fillStyle = 'red';
		context.strokeStyle = 'red';
		context.lineWidth = 1;
		for (lonlat of StationCoordinates.map(v => v.filter((_, i) => i !== 0))) {
			geoStation.center(lonlat);
			context.beginPath();
			geoGenerator(geoStation());
			context.fill();
			context.stroke();
		}
		
	}

	d3.json(geojson_url)
	.then(function(data) {
		geojson = topojson.feature(data, data.objects.land);
		window.setInterval(update, 1000 / fps);
	})

}

main();
