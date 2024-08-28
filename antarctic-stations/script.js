
let land_path = './maps/land-50m.json';  // topojson
let land;
d3.json(land_path)
.then(function(data) {
	land = topojson.feature(data, data.objects.land);
})

let iceshelves_path = './maps/ne_50m_antarctic_ice_shelves_polys.json';  // geojson
let iceshelves;
d3.json(iceshelves_path)
.then(function(data) {
	iceshelves = data;
})

let exclude_types = [];

async function main() {
	
	let scrape_path = './scrape_data.json';
	const response = await fetch(scrape_path);
	const data = await response.json();

	let country_data = {};
	for (d of data) {
		let country = Object.keys(d);
		country_data[country] = d[country];
	}
	
	for (country of Object.keys(country_data)) {
		country_data[country]['display'] = true;
	}

	canvas.width = 1600;
	canvas.height = 1200;

	let context = d3.select('#canvas')
	.node()
	.getContext('2d');

	let projection = d3.geoAzimuthalEquidistant()
	.rotate([0, 90])
	.scale(canvas.height * 0.95)
	.translate([canvas.width / 2, canvas.height / 2]);

	let graticule = d3.geoGraticule();
	let geoGenerator = d3.geoPath(projection, context);
	let geoStation = d3.geoCircle();
	
	function drawMap(exclude_types=[]) {

		context.clearRect(0, 0, canvas.width, canvas.height);

		for (country of Object.keys(country_data)) {
			if (country_data[country]['display']) {
				context.lineWidth = 1.5;
				if (country_data[country]['items'].length > 0) {
					for (item of country_data[country]['items']) {
						if (exclude_types.includes(item['TYPE']) == false) {
							context.fillStyle = country_data[country]['color'];
							context.strokeStyle = 'white';
							if (item['TYPE'] == 'Station') {
								geoStation.radius(0.6);
								context.globalCompositeOperation = 'source-over';
							}
							else if (item['TYPE'] == 'Automatic Recording Station') {
								geoStation.radius(0.2);
								context.globalCompositeOperation = 'destination-over';
							}
							else {  // misc camps
								geoStation.radius(0.4);
								context.globalCompositeOperation = 'destination-over';
							}
							geoStation.center([item['LON'], item['LAT']]);
							context.beginPath();
							geoGenerator(geoStation());
							context.fill();
							context.stroke();
						}
					}
				}
			}
		}
		
		context.globalCompositeOperation = 'destination-over';
		
		context.beginPath();
		geoGenerator(graticule());
		context.strokeStyle = '#a9a9a9';
		context.lineWidth = 2;
		context.stroke();

		context.beginPath();
		geoGenerator({type: 'FeatureCollection', features: land.features})
		context.fillStyle = 'white';
		context.fill();
		
		context.beginPath();
		geoGenerator({type: 'FeatureCollection', features: iceshelves.features})
		context.fillStyle = '#e8f4f8';
		context.fill();
	
	}
	
	drawMap(exclude_types);

	var tooltip = document.getElementById('tooltip');
	d3.select('canvas').on('mousemove', (event) => {
		const { width, height } = canvas.getBoundingClientRect();
		let mouse = projection.invert([d3.pointer(event)[0] * canvas.width / width, 
		                               d3.pointer(event)[1] * canvas.height / height]);
		let tooltipHTML = '';
		let tooltipOn = false;
		for (country of Object.keys(country_data)) {
			if (country_data[country]['items'].length > 0) {
				for (item of country_data[country]['items']) {
					if (exclude_types.includes(item['TYPE']) == false) {
						let pointer_distance = 0.007;
						if (item['TYPE'] == 'Station') { pointer_distance = 0.01; }
						else if (item['TYPE'] == 'Automatic Recording Station') { pointer_distance = 0.004; }
						if (d3.geoDistance(mouse, [item['LON'], item['LAT']]) < pointer_distance) {
							if (country_data[country]['display'] == true) {
								if (tooltipOn == true) {
									tooltipHTML += '<hr>';
								}
								tooltipHTML += item['NAME'] + '<br><i>' + item['TYPE'] + '</i><br><b>' + country + '</b><br>';
								tooltipOn = true;
							}
						}
					}
				}
			}
		}
		if (tooltipOn == false) {
			tooltip.innerHTML = '';
			tooltip.style.display = 'none';
		}
		else {
			tooltip.innerHTML = tooltipHTML;
			tooltip.style.display = 'block';
			let xoffset = event.pageX;
			let yoffset = event.pageY;
			if (mouse[0] > 0) {  // right half of page
				xoffset -= tooltip.offsetWidth;
			}
			if (Math.abs(mouse[0]) > 90) {  // bottom half of page
				yoffset -= tooltip.offsetHeight;
			}
			tooltip.style.left = xoffset + 'px';
			tooltip.style.top = yoffset + 'px';
		}
	})
	
	let flag_height = 'calc((90vmin / ' + (Object.keys(country_data).length / 2).toString() + ') - 0.5vmin)';
	let flag_width = 'calc((120vmin / ' + (Object.keys(country_data).length / 2).toString() + ') - 0.5vmin)';
	var flags = document.getElementById('flags');
	flags.style.width = 'calc(2 * ' + flag_width + ' + 1.0vmin)';
	for (country of Object.keys(country_data)) {
		flags.innerHTML += '<img class="flag" id="flag-' + country + 
		                   '" src="./flags/' + country_data[country]['code'] + '.svg"' +
						   'title="' + country + '"></img>';
		let flag = document.getElementById('flag-' + country);
		flag.style.height = flag_height;
		flag.style.width = flag_width;
		flag.style.margin = '0.25vmin';
	}
	function toggleCountry(country) {
		let flag = document.getElementById('flag-' + country);
		if (country_data[country]['display'] == true) {
			country_data[country]['display'] = false;
			flag.style.opacity = 0.6;
		}
		else if (country_data[country]['display'] == false) {
			country_data[country]['display'] = true;
			flag.style.opacity = 1.0;
		}
	}
	for (flag of document.getElementsByClassName('flag')) {
		flag.addEventListener('click', function (event) {
			let country = event.target.id.split('-').slice(1)[0];
			toggleCountry(country);
			drawMap(exclude_types);
		})
	}
	
	var toolbar = document.getElementById('toolbar');
	function toggleCountries() {
		for (country of Object.keys(country_data)) {
			country_data[country]['display'] = false;
			document.getElementById('flag-' + country).style.opacity = 0.6;
		}
	}
	toolbar.innerHTML += '<span>toggle all:</span>'
	toolbar.innerHTML += '<span class="toggle">' +
	                     '<input id="toggle-stations" type="checkbox" checked>' +
						 '<label for="toggle-stations">main<br>stations</label>' +
						 '</span>';
	toolbar.innerHTML += '<span class="toggle">' +
	                     '<input id="toggle-camps" type="checkbox" checked>' +
						 '<label for="toggle-camps">field<br>camps</label>' +
						 '</span>';
	toolbar.innerHTML += '<span class="toggle">' +
	                     '<input id="toggle-ars" type="checkbox" checked>' +
						 '<label for="toggle-ars">automated<br>stations</label>' +
						 '</span>';
	toolbar.innerHTML += '<span class="toggle">' +
	                     '<input id="toggle-countries" type="checkbox" checked>' +
						 '<label for="toggle-countries">countries</label>' +
						 '</span>';
	document.getElementById('toggle-stations').addEventListener('change', function(event) {
		if (event.target.checked) {
			exclude_types = exclude_types.filter(e => e !== 'Station');
		}
		else {
			exclude_types.push('Station');
		}
		drawMap(exclude_types)
	})
	document.getElementById('toggle-camps').addEventListener('change', function(event) {
		for (camp_type of ['Camp', 'Refuge', 'Depot', 'Laboratory', 'Airfield Camp']) {
			if (event.target.checked) {
				exclude_types = exclude_types.filter(e => e !== camp_type);
			}
			else {
				exclude_types.push(camp_type);
			}
		}
		drawMap(exclude_types)
	})
	document.getElementById('toggle-ars').addEventListener('change', function(event) {
		if (event.target.checked) {
			exclude_types = exclude_types.filter(e => e !== 'Automatic Recording Station');
		}
		else {
			exclude_types.push('Automatic Recording Station');
		}
		drawMap(exclude_types)
	})
	document.getElementById('toggle-countries').addEventListener('change', function(event) {
		for (country of Object.keys(country_data)) {
			if (event.target.checked) {
				if (country_data[country]['display'] == false) {
					toggleCountry(country);
				}
			}
			else {
				if (country_data[country]['display'] == true) {
					toggleCountry(country);
				}
			}
		}
		drawMap(exclude_types);
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
	
	function positionFlags() {
		if (canvas.getBoundingClientRect().left > 0) {
			flags.style.right = canvas.getBoundingClientRect().left + 'px';
		}
		else {
			flags.style.right = 0;
		}
	}
	function positionToolbar() {
		toolbar.style.bottom = canvas.getBoundingClientRect().top + 'px';
	}
	function positionInfo() {
		info.style.transition = '';
		if (canvas.getBoundingClientRect().left > 0) {
			info.style.left = canvas.getBoundingClientRect().left + 'px';
		}
		else {
			info.style.left = 0;
		}
		info.style.top = canvas.getBoundingClientRect().top + 'px';
	}
	positionFlags();
	positionToolbar();
	positionInfo();
	window.addEventListener('resize', function (event) {
		positionFlags();
		positionToolbar();
		positionInfo();
	})
	
	toolbar.style.visibility = 'visible';
	info.style.visibility = 'visible';

	document.getElementById('loading').remove();
}

main();
