
async function main() {
	
	async function loadData() {

		let scrape_path = './processing/airline_data.json';
		const response = await fetch(scrape_path);
		const data = await response.json();
		let years = Object.keys(data);
		let airline_data = {};
		for (year of years) {
			airline_data[year] = data[year];
		}
		
		let land_path = './maps/land-50m.json';  // topojson
		let land_data;
		await d3.json(land_path)
		.then(function(data) {
			land_data = topojson.feature(data, data.objects.land);
		})

		return [airline_data, land_data];

	}
	
	let [airline_data, land_data] = await loadData();
	
	let exclude_types = [];

	canvas.width = 1600;
	canvas.height = 1200;

	let context = d3.select('#canvas')
	.node()
	.getContext('2d');

	let projection = d3.geoAzimuthalEquidistant()
	.rotate([90, -45])
	.scale(canvas.height * 0.5)
	.translate([canvas.width / 2, canvas.height / 2]);

	let graticule = d3.geoGraticule();
	let geoGenerator = d3.geoPath(projection, context);
	let geoAirport = d3.geoCircle();
	
	let colors = d3.scaleSequential(d3.interpolateViridis);
	
	let all_years = Object.keys(airline_data);
	
	function drawMap(years) {
		
		console.log(years)

		context.clearRect(0, 0, canvas.width, canvas.height);
		
		context.beginPath();
		geoGenerator({type: 'FeatureCollection', features: land_data.features})
		context.fillStyle = 'white';
		context.fill();
		
		context.beginPath();
		geoGenerator(graticule());
		context.strokeStyle = '#a9a9a9';
		context.lineWidth = 2;
		context.stroke();

		geoAirport.radius(0.5);
		context.strokeStyle = 'black';
		context.lineWidth = 0.5;
		for (year of years) {
			let color_idx = (year - Math.min(...all_years)) / (all_years.length - 1);
			context.beginPath();
			context.fillStyle = colors(color_idx);
			for (airline of Object.keys(airline_data[year])) {
				for (airport of Object.keys(airline_data[year][airline])) {
					let lat = airline_data[year][airline][airport]['lat'];
					let lon = airline_data[year][airline][airport]['lon'];
					geoAirport.center([lon, lat]);
					geoGenerator(geoAirport());
				}
			}
			context.fill();
			context.stroke();
		}
	
	}
	
	// https://medium.com/@predragdavidovic10/native-dual-range-slider-html-css-javascript-91e778134816
	document.getElementById('yearRangeHigh').min = Math.min(...all_years)
	document.getElementById('yearRangeHigh').max = Math.max(...all_years)
	document.getElementById('yearRangeHigh').value = Math.max(...all_years)
	document.getElementById('yearRangeLow').min = Math.min(...all_years)
	document.getElementById('yearRangeLow').max = Math.max(...all_years)
	document.getElementById('yearRangeLow').value = Math.min(...all_years)
	document.getElementById('yearRangeHigh').addEventListener('input', function (event) {
		adjustSlider()
	})
	document.getElementById('yearRangeLow').addEventListener('input', function (event) {
		adjustSlider()
	})
	function fillSlider(from, to, sliderColor, rangeColor, controlSlider) {
		let rangeDistance = to.max - to.min;
		let fromPosition = from.value - to.min;
		let toPosition = to.value - to.min;
		if (fromPosition > toPosition) {
			let [tmpFrom, tmpTo] = [fromPosition, toPosition];
			fromPosition = tmpTo;
			toPosition = tmpFrom;
		}
		controlSlider.style.background = `linear-gradient(to right,
			${sliderColor} 0%,
			${sliderColor} ${(fromPosition)/(rangeDistance)*100}%,
			${rangeColor} ${((fromPosition)/(rangeDistance))*100}%,
			${rangeColor} ${(toPosition)/(rangeDistance)*100}%,
			${sliderColor} ${(toPosition)/(rangeDistance)*100}%,
			${sliderColor} 100%)`;
		return [fromPosition, toPosition];
	}
	function adjustSlider() {
		let fromInput = document.getElementById('yearRangeLow');
		let toInput = document.getElementById('yearRangeHigh');
		let controlSlider = document.getElementById('yearRangeHigh');
		let [fromPosition, toPosition] = fillSlider(fromInput, toInput, 'lightgray', 'black', controlSlider);
		let years = Object.keys(airline_data).slice(fromPosition, toPosition + 1);
		document.getElementById('fromYear').innerText = years[0];
		document.getElementById('toYear').innerText = years.slice(-1);
		drawMap(years);
	}
	adjustSlider()

}

main();
