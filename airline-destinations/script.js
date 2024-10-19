
var possible_airlines = ['UA', 'DL', 'AA', 'AS', 'WN'].sort();
var chosen_airline = possible_airlines[possible_airlines.length * Math.random() | 0]
var toggle_routes = document.getElementById('toggle-routes').checked;
var toggle_citystate = document.getElementById('toggle-citystate').checked;

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
		for (line of L_UNIQUE_CARRIERS.split('\r\n')) {
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
		for (line of L_AIRPORT.split('\r\n')) {
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

		let context = d3.select('#canvas')
		.node()
		.getContext('2d');

		let projection = d3.geoOrthographic()
		.rotate([90, -45])
		.scale(canvas.height * 0.66)
		.translate([canvas.width / 2, canvas.height / 2]);

		let graticule = d3.geoGraticule();
		let geoGenerator = d3.geoPath(projection, context);
		let geoAirport = d3.geoCircle();
		
		function drawMap(years, chosen_airline) {
			
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
				for (airline of Object.keys(airline_data[year])) {
					let routes_plotted = [];
					for (year of years) {
						if ((airline == chosen_airline) & Object.keys(airline_data[year]).includes(airline)) {
							let color_idx = (year - Math.min(...all_years)) / (all_years.length - 1);
							context.beginPath();
							context.strokeStyle = colors(color_idx);
							for (route of airline_data[year][airline]['route_pairs']) {
								if (routes_plotted.includes(route) == false) {
									routes_plotted.push(route);
									let [airport1, airport2] = route.split('-');
									let lat1 = airline_data[year][airline][airport1]['lat'];
									let lon1 = airline_data[year][airline][airport1]['lon'];
									let lat2 = airline_data[year][airline][airport2]['lat'];
									let lon2 = airline_data[year][airline][airport2]['lon'];
									geoGenerator({type: 'LineString', coordinates: [[lon1, lat1], [lon2, lat2]]});
								}
							}
							context.stroke();
						}
					}
				}
			}

			geoAirport.radius(0.5);
			context.strokeStyle = 'black';
			context.lineWidth = 1.0;
			for (airline of Object.keys(airline_data[year])) {
				let airports_plotted = [];
				for (year of years) {
					if ((airline == chosen_airline) & Object.keys(airline_data[year]).includes(airline)) {
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
				if (airline == chosen_airline) {
					let chosen_airline_str = airline_lookup[chosen_airline];
					document.getElementById('airlineInfo').innerText = 'Airline: ' + chosen_airline_str + '\n' +
																	   'Destinations: ' + airports_plotted.length;
				}
			}

		}
		
		drawMap(years, chosen_airline);
		
		return [drawMap, projection];
	
	}
	
	let [drawMap, projection] = initMap(all_years, chosen_airline);
	
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
		let tooltipHTML = '';
		let tooltipOn = false;
		for (year of years) {
			for (airline of Object.keys(airline_data[year])) {
				if ((airline == chosen_airline) & Object.keys(airline_data[year]).includes(airline)) {
					for (airport of Object.keys(airline_data[year][airline])) {
						let pointer_distance = 0.009;
						let lat = airline_data[year][airline][airport]['lat'];
						let lon = airline_data[year][airline][airport]['lon'];
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
								tooltipOn = true;
							}
						}
						
					}
				}
			}
		}
		if (tooltipOn == false) {
			let tooltipAirports = [];
			tooltip.innerHTML = '';
			tooltip.style.display = 'none';
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
	for (airline of possible_airlines) {
		info_text.innerHTML += '<button id="button-' + airline + '" type="button">' + 
		                       '(' + airline + ') ' + airline_lookup[airline] + '</button><br>';
	}
	for (airline of possible_airlines) {
		document.getElementById('button-' + airline).addEventListener('click', function (event) {
			chosen_airline = event.target.id.split('-')[1];
			drawMap(years, chosen_airline);
		})
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
		let rotation = projection.rotate().map(function (num, idx) {
			return num + [0, -rotationMagnitude, 0][idx];
		})
		projection.rotate(rotation);
		drawMap(years, chosen_airline);
	})
	document.getElementById('controls-down').addEventListener('click', function (event) {
		let rotation = projection.rotate().map(function (num, idx) {
			return num + [0, +rotationMagnitude, 0][idx];
		})
		projection.rotate(rotation);
		drawMap(years, chosen_airline);
	})
	document.getElementById('controls-left').addEventListener('click', function (event) {
		let rotation = projection.rotate().map(function (num, idx) {
			return num + [+rotationMagnitude, 0, 0][idx];
		})
		projection.rotate(rotation);
		drawMap(years, chosen_airline);
	})
	document.getElementById('controls-right').addEventListener('click', function (event) {
		let rotation = projection.rotate().map(function (num, idx) {
			return num + [-rotationMagnitude, 0, 0][idx];
		})
		projection.rotate(rotation);
		drawMap(years, chosen_airline);
	})
	document.getElementById('controls-in').addEventListener('click', function (event) {
		let scale = projection.scale() + scaleMagnitude;
		projection.scale(scale);
		drawMap(years, chosen_airline);
	})
	document.getElementById('controls-out').addEventListener('click', function (event) {
		let scale = projection.scale() - scaleMagnitude;
		projection.scale(scale);
		drawMap(years, chosen_airline);
	})
	
	window.addEventListener('resize', function (event) {
		drawMap(years, chosen_airline);
	})

}

main();
