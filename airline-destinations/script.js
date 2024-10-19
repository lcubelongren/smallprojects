
// including airlines from https://en.wikipedia.org/wiki/List_of_airlines_of_the_United_States
const possible_airlines = {
	'mainline': ['AA', 'AS', 'B6', 'DL', 'F9', 'G4', 'HA', 'MX', 'NK', 'SY', 'UA', 'WN', 'XP'].sort(),
	'regional': ['3M', '9E', '9K', 'C5', 'G7', 'MQ', 'OH', 'OO', 'PT', 'QX', 'YV', 'YX', 'ZW'].sort(),
	'cargo': ['5V', '5X', '7S', 'EM', 'FX', 'KH', 'KO', 'L2', 'M6', 'NC'].sort(),
};
const possible_airlines_flat = Object.values(possible_airlines).flat();
var chosen_airline = possible_airlines_flat[possible_airlines_flat.length * Math.random() | 0];

var toggle_routes = document.getElementById('toggle-routes').checked;
var toggle_citystate = document.getElementById('toggle-citystate').checked;

var rotation = [90, -45];
var scale = window.innerHeight * 0.66;

async function main() {
	
	async function loadData() {

		let data_path = './processing/airline_data.json';
		let data_response = await fetch(data_path);
		let data = await data_response.json();
		let years = Object.keys(data);
		let airline_data = {};
		for (year of years) {
			airline_data[year] = data[year];
		}
		
		let L_UNIQUE_CARRIERS_path = './data/lookups/L_UNIQUE_CARRIERS.csv';
		let L_UNIQUE_CARRIERS_response = await fetch(L_UNIQUE_CARRIERS_path);
		let L_UNIQUE_CARRIERS = await L_UNIQUE_CARRIERS_response.text();
		let airline_lookup = {};
		for (line of L_UNIQUE_CARRIERS.split('\n')) {
			if (line.split(',').length > 1) {
				let [code, description] = line.split(',');
				code = code.replace(/"/g, '');
				description = description.replace(/"/g, '');
				airline_lookup[code] = description;
			}
		}
		
		let L_AIRPORT_path = './data/lookups/L_AIRPORT.csv';
		let L_AIRPORT_response = await fetch(L_AIRPORT_path);
		let L_AIRPORT = await L_AIRPORT_response.text();
		let airport_lookup = {};
		for (line of L_AIRPORT.split('\n')) {
			if (line.split('"').length > 3) {
				let code = line.split('"')[1];
				let description = line.split('"')[3].split(':')[0];
				airport_lookup[code] = description;
			}
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

		return [airline_data, airline_lookup, airport_lookup, land_data, lake_data];

	}
	
	let [airline_data, airline_lookup, airport_lookup, land_data, lake_data] = await loadData();
	
	let all_years = Object.keys(airline_data);
	
	let colors = d3.scaleSequential(d3.interpolateWarm);
	
	function initMap(years, chosen_airline) {
		
		canvas.width = window.innerWidth;
		canvas.height = window.innerHeight;
		canvasoverlay.width = window.innerWidth;
		canvasoverlay.height = window.innerHeight;

		let context = d3.select('#canvas')
		.node()
		.getContext('2d');
		let contextoverlay = d3.select('#canvasoverlay')
		.node()
		.getContext('2d');

		let projection = d3.geoOrthographic()
		let graticule = d3.geoGraticule();
		let geoGenerator = d3.geoPath(projection, context);
		let geoAirport = d3.geoCircle();
		
		function drawMap(years, chosen_airline) {
			
			projection
			.rotate(rotation)
			.scale(scale)
			.translate([canvas.width / 2, canvas.height / 2]);
			
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
			context.lineWidth = 1.5;
			context.stroke();
			
			if (toggle_routes) {
				context.lineWidth = 0.5;
				let routes_plotted = [];
				for (year of years) {
					if (Object.keys(airline_data[year]).includes(chosen_airline)) {
						let color_idx = (year - Math.min(...all_years)) / (all_years.length - 1);
						context.beginPath();
						context.strokeStyle = colors(color_idx);
						for (route of airline_data[year][chosen_airline]['route_pairs']) {
							if (routes_plotted.includes(route) == false) {
								routes_plotted.push(route);
								let [airport1, airport2] = route.split('-');
								let lat1 = airline_data[year][chosen_airline][airport1]['lat'];
								let lon1 = airline_data[year][chosen_airline][airport1]['lon'];
								let lat2 = airline_data[year][chosen_airline][airport2]['lat'];
								let lon2 = airline_data[year][chosen_airline][airport2]['lon'];
								geoGenerator({type: 'LineString', coordinates: [[lon1, lat1], [lon2, lat2]]});
							}
						}
						context.stroke();
					}
				}
			}

			geoAirport.radius(0.5);
			context.strokeStyle = 'black';
			context.lineWidth = 1.0;
			let airports_plotted = [];
			for (year of years) {
				if (Object.keys(airline_data[year]).includes(chosen_airline)) {
					let color_idx = (year - Math.min(...all_years)) / (all_years.length - 1);
					context.beginPath();
					context.fillStyle = colors(color_idx);
					for (airport of Object.keys(airline_data[year][chosen_airline])) {
						if (airports_plotted.includes(airport) == false) {
							airports_plotted.push(airport);
							let lat = airline_data[year][chosen_airline][airport]['lat'];
							let lon = airline_data[year][chosen_airline][airport]['lon'];
							geoAirport.center([lon, lat]);
							geoGenerator(geoAirport());
						}
					}
					context.fill();
					context.stroke();
				}
			}
			let airline_name = airline_lookup[chosen_airline];
			airline_name = airline_name.split('d/b/a')[0];
			airline_name = airline_name.split('dba')[0];
			airline_name = airline_name.split('DBA')[0];
			airline_name = airline_name.trim();
			document.getElementById('airlineInfo').innerText = 'Airline: ' + airline_name + '\n' +
															   'Destinations: ' + airports_plotted.length;

		}
		
		drawMap(years, chosen_airline);
		
		return [drawMap, projection, context, contextoverlay];
	
	}
	
	let [drawMap, projection, context, contextoverlay] = initMap(all_years, chosen_airline);
	
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
		drawMap(years, chosen_airline);
		return years;
	}
	let fromInput = document.getElementById('yearRangeLow');
	let toInput = document.getElementById('yearRangeHigh');
	fromInput.min = Math.min(...all_years);
	fromInput.max = Math.max(...all_years);
	fromInput.value = Math.min(...all_years);
	toInput.min = Math.min(...all_years);
	toInput.max = Math.max(...all_years);
	toInput.value = Math.max(...all_years);
	var years = adjustSlider(fromInput, toInput);
	document.getElementById('yearRangeHigh').addEventListener('input', function (event) {
		years = adjustSlider(fromInput, toInput);
	})
	document.getElementById('yearRangeLow').addEventListener('input', function (event) {
		years = adjustSlider(fromInput, toInput);
	})
	
	var tooltip = document.getElementById('tooltip');
	d3.select('canvas').on('mousemove', (event) => {
		const { width, height } = canvas.getBoundingClientRect();
		let mouse = projection.invert([d3.pointer(event)[0] * canvas.width / width, 
		                               d3.pointer(event)[1] * canvas.height / height]);
		let tooltipAirports = [];
		let tooltipRoutes = {};
		let tooltipHTML = '';
		let tooltipOn = false;
		for (year of years) {
			tooltipRoutes[year] = [];
			if (Object.keys(airline_data[year]).includes(chosen_airline)) {
				for (airport of Object.keys(airline_data[year][chosen_airline])) {
					let pointer_distance = 0.009;
					let lat = airline_data[year][chosen_airline][airport]['lat'];
					let lon = airline_data[year][chosen_airline][airport]['lon'];
					if (d3.geoDistance(mouse, [lon, lat]) < pointer_distance) {
						if (tooltipAirports.includes(airport) == false) {
							if (tooltipOn == true) {
								tooltipHTML += '<hr>';
							}
							if (toggle_citystate) {
								tooltipHTML += '<b>' + airport + '</b>' + ' - ' + airport_lookup[airport];
							}
							else {
								tooltipHTML += '<b>' + airport + '</b>';
							}
							tooltipAirports.push(airport);
						}
						for (route of airline_data[year][chosen_airline]['route_pairs']) {
							let [airport1, airport2] = route.split('-');
							if ((airport == airport1) | (airport == airport2)) {
								if ((Object.values(tooltipRoutes).flat().includes(airport1 + '-' + airport2) == false) &
									(Object.values(tooltipRoutes).flat().includes(airport2 + '-' + airport1) == false)) {
									tooltipRoutes[year].push(route);
								}
							}
						}
					tooltipOn = true;
					}
				}
			}
		}
		let tooltipAirport = d3.geoCircle();
		let tooltipGenerator = d3.geoPath(projection, contextoverlay);
		if (tooltipOn == false) {
			let tooltipAirports = [];
			tooltip.innerHTML = '';
			tooltip.style.display = 'none';
			contextoverlay.clearRect(0, 0, canvasoverlay.width, canvasoverlay.height);
		}
		else {
			tooltip.innerHTML = tooltipHTML;
			tooltip.style.display = 'block';
			let xoffset = event.pageX;
			let yoffset = event.pageY;
			xoffset -= tooltip.offsetWidth;
			yoffset -= tooltip.offsetHeight;
			tooltip.style.left = xoffset + 'px';
			tooltip.style.top = yoffset + 'px';
			if (toggle_routes) {
				for (year of years) {
					for (route of tooltipRoutes[year]) {
						if (Object.keys(airline_data[year]).includes(chosen_airline)) {
							let [airport1, airport2] = route.split('-');
							let lat1 = airline_data[year][chosen_airline][airport1]['lat'];
							let lon1 = airline_data[year][chosen_airline][airport1]['lon'];
							let lat2 = airline_data[year][chosen_airline][airport2]['lat'];
							let lon2 = airline_data[year][chosen_airline][airport2]['lon'];
							contextoverlay.beginPath();
							tooltipGenerator({type: 'LineString', coordinates: [[lon1, lat1], [lon2, lat2]]});
							contextoverlay.lineWidth = 2.0
							contextoverlay.strokeStyle = 'black';
							contextoverlay.stroke();
							contextoverlay.beginPath();
							contextoverlay.fillStyle = 'black';
							tooltipAirport.radius(0.5);
							for (airport of tooltipAirports) {
								let lat = airline_data[year][chosen_airline][airport]['lat'];
								let lon = airline_data[year][chosen_airline][airport]['lon'];
								tooltipAirport.center([lon, lat]);
								tooltipGenerator(tooltipAirport());
							}
							contextoverlay.fill()
						}
					}
				}
			}
		}
	})
	
	let info = document.getElementById('info');
	info.addEventListener('click', function (event) {
		info.style.transition = 'all 0.3s ease-out';
		if (info.className == '') {
			info.className = 'active';
		}
		else {
			info.className = '';
		}
	})
	info.style.transition = '';
	info.style.visibility = 'visible';
	let info_text = document.getElementById('info-text');
	info_text.innerHTML = '';
	for (airline_type of Object.keys(possible_airlines)) {
		info_text.innerHTML += airline_type + ' airlines';
		for (airline of possible_airlines[airline_type]) {
			let airline_name = airline_lookup[airline];
			airline_name = airline_name.split('d/b/a')[0];
			airline_name = airline_name.split('dba')[0];
			airline_name = airline_name.split('DBA')[0];
			airline_name = airline_name.trim();
			info_text.innerHTML += '<button id="button-' + airline + '" type="button">' + 
								   '(' + airline + ') ' + airline_name + '</button><br>';
		}
	}
	for (airline_type of Object.keys(possible_airlines)) {
		for (airline of possible_airlines[airline_type]) {
			document.getElementById('button-' + airline).addEventListener('click', function (event) {
				chosen_airline = event.target.id.split('-')[1];
				drawMap(years, chosen_airline);
			})
		}
	}
	
	document.getElementById('toggle-routes').addEventListener('click', function (event) {
		if (toggle_routes) {
			toggle_routes = false;
		}
		else {
			toggle_routes = true;
		}
		drawMap(years, chosen_airline);
	})
	document.getElementById('toggle-citystate').addEventListener('click', function (event) {
		if (toggle_citystate) {
			toggle_citystate = false;
		}
		else {
			toggle_citystate = true;
		}
		drawMap(years, chosen_airline);
	})
	
	let rotationMagnitude = 7.5;
	let scaleMagnitude = 50;
	document.getElementById('controls-up').addEventListener('click', function (event) {
		rotation = rotation.map(function (num, idx) {
			return num + [0, -rotationMagnitude, 0][idx];
		})
		projection.rotate(rotation);
		drawMap(years, chosen_airline);
	})
	document.getElementById('controls-down').addEventListener('click', function (event) {
		rotation = rotation.map(function (num, idx) {
			return num + [0, +rotationMagnitude, 0][idx];
		})
		projection.rotate(rotation);
		drawMap(years, chosen_airline);
	})
	document.getElementById('controls-left').addEventListener('click', function (event) {
		rotation = rotation.map(function (num, idx) {
			return num + [+rotationMagnitude, 0, 0][idx];
		})
		projection.rotate(rotation);
		drawMap(years, chosen_airline);
	})
	document.getElementById('controls-right').addEventListener('click', function (event) {
		rotation = rotation.map(function (num, idx) {
			return num + [-rotationMagnitude, 0, 0][idx];
		})
		projection.rotate(rotation);
		drawMap(years, chosen_airline);
	})
	document.getElementById('controls-in').addEventListener('click', function (event) {
		scale = scale + scaleMagnitude;
		projection.scale(scale);
		drawMap(years, chosen_airline);
	})
	document.getElementById('controls-out').addEventListener('click', function (event) {
		scale = scale - scaleMagnitude;
		projection.scale(scale);
		drawMap(years, chosen_airline);
	})
	
	window.addEventListener('resize', function (event) {
		initMap(years, chosen_airline);
	})

}

main();
