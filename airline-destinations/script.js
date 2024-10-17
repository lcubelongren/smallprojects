
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
		
		let lake_path = './maps/ne_110m_lakes.json';  // geojson
		let lake_data;
		await d3.json(lake_path)
		.then(function(data) {
			lake_data = data;
		})

		return [airline_data, land_data, lake_data];

	}
	
	let [airline_data, land_data, lake_data] = await loadData();
	
	canvas.width = window.innerWidth;
	canvas.height = window.innerHeight;

	let context = d3.select('#canvas')
	.node()
	.getContext('2d');

	let projection = d3.geoAzimuthalEquidistant()
	.rotate([90, -45])
	.scale(canvas.height * 0.66)
	.translate([canvas.width / 2, canvas.height / 2]);

	let graticule = d3.geoGraticule();
	let geoGenerator = d3.geoPath(projection, context);
	let geoAirport = d3.geoCircle();
	
	let colors = d3.scaleSequential(d3.interpolateViridis);
	
	let all_years = Object.keys(airline_data);
	
	function drawMap(years) {
		
		context.clearRect(0, 0, canvas.width, canvas.height);
		
		context.beginPath();
		geoGenerator({type: 'FeatureCollection', features: land_data.features})
		context.fillStyle = 'white';
		context.fill();
		
		context.beginPath();
		geoGenerator({type: 'FeatureCollection', features: lake_data.features})
		context.fillStyle = 'black';
		context.fill();
		
		context.beginPath();
		geoGenerator(graticule());
		context.strokeStyle = '#a9a9a9';
		context.lineWidth = 2;
		context.stroke();

		geoAirport.radius(0.5);
		context.strokeStyle = 'black';
		context.lineWidth = 1.0;
		for (airline of Object.keys(airline_data[year])) {
			let airports_plotted = [];
			let include_airlines = ['UA'];
			for (year of years) {
				if (include_airlines.includes(airline) & Object.keys(airline_data[year]).includes(airline)) {
					let color_idx = (year - Math.min(...all_years)) / (all_years.length - 1);
					context.beginPath();
					context.fillStyle = colors(color_idx);
					for (airport of Object.keys(airline_data[year][airline])) {
						if (airports_plotted.includes(airport) == false) {
							airports_plotted.push(airport);
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
			if (include_airlines.includes(airline)) {
				document.getElementById('airlineInfo').innerText = 'Airline: ' + include_airlines[0] + '\n' +
				                                                   'Destinations: ' + airports_plotted.length;
			}
		}
	
	}
	
	// https://medium.com/@predragdavidovic10/native-dual-range-slider-html-css-javascript-91e778134816
	function fillSlider(from, to, sliderColor) {
		let rangeDistance = to.max - to.min;
		let fromPosition = from.value - to.min;
		let toPosition = to.value - to.min;
		if (fromPosition > toPosition) {
			let [tmpFrom, tmpTo] = [fromPosition, toPosition];
			fromPosition = tmpTo;
			toPosition = tmpFrom;
		}
		let fillString = `linear-gradient(to right,
			${sliderColor} 0%,
			${sliderColor} ${(fromPosition)/(rangeDistance)*100}%,`
		for (var i=0; i <= (toPosition - fromPosition); i++) {
			let fillPosition = fromPosition + i;
			let fillColor = colors(fillPosition / rangeDistance);
			fillString += `\n${fillColor} ${((fillPosition)/(rangeDistance))*100}%,`;
		}
		fillString += `\n${sliderColor} ${(toPosition)/(rangeDistance)*100}%,
			${sliderColor} 100%)`;
		to.style.background = fillString;
		return [fromPosition, toPosition, rangeDistance];
	}
	function adjustSlider(fromInput, toInput) {
		let [fromPosition, toPosition, rangeDistance] = fillSlider(fromInput, toInput, '#a9a9a9');
		let years = all_years.slice(fromPosition, toPosition + 1);
		document.getElementById('fromYear').innerText = years[0];
		document.getElementById('toYear').innerText = years.slice(-1);
		document.getElementById('fromYear').style.color = colors(fromPosition / rangeDistance);
		document.getElementById('toYear').style.color = colors(toPosition / rangeDistance);
		drawMap(years);
	}
	let fromInput = document.getElementById('yearRangeLow');
	let toInput = document.getElementById('yearRangeHigh');
	fromInput.min = Math.min(...all_years)
	fromInput.max = Math.max(...all_years)
	fromInput.value = Math.min(...all_years)
	toInput.min = Math.min(...all_years)
	toInput.max = Math.max(...all_years)
	toInput.value = Math.max(...all_years)
	adjustSlider(fromInput, toInput)
	document.getElementById('yearRangeHigh').addEventListener('input', function (event) {
		adjustSlider(fromInput, toInput);
	})
	document.getElementById('yearRangeLow').addEventListener('input', function (event) {
		adjustSlider(fromInput, toInput);
	})

}

main();

window.addEventListener('resize', function (event) {
	main();
})
