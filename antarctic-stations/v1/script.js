
//https://www.ats.aq/devAS/InformationExchange/ArchivedInformation
//https://www.ats.aq/devAS/InformationExchange/LatestReports

//let dir = './reports/2022_2023/';
//let fname = 'Annual report - 2022_2023 - Report - <COUNTRY>.html';
let dir = './reports/Permanent_information/';
let fname = 'Permanent information - Report - <COUNTRY>.html';
let countries = {  // https://vexillogasm.com/country-flags/
	'Argentina': {'color': '#74ACDF', 'code': 'ar'},
	'Australia': {'color': '#00008B', 'code': 'au'},
	'Belarus': {'color': '#C8102E', 'code': 'by'},
	'Belgium': {'color': '#FCD116', 'code': 'be'},
	'Brazil': {'color': '#009B3A', 'code': 'br'},
	'Bulgaria': {'color': '#00966E', 'code': 'bg'},
	'Canada': {'color': '#FF0000', 'code': 'ca'},
	'Chile': {'color': '#0039A6', 'code': 'cl'},
	'China': {'color': '#DE2910', 'code': 'cn'},
	'Colombia': {'color': '#FCD116', 'code': 'co'},
	'Czechia': {'color': '#11457E', 'code': 'cz'},
	'Ecuador': {'color': '#FCDD09', 'code': 'ec'},
	'Finland': {'color': '#003580', 'code': 'fi'},
	'France': {'color': '#002395', 'code': 'fr'},
	'Germany': {'color': '#FFCE00', 'code': 'de'},
	'India': {'color': '#FF9933', 'code': 'in'},
	'Italy': {'color': '#009246', 'code': 'it'},
	'Japan': {'color': '#BC002D', 'code': 'jp'},
	'Korea (ROK)': {'color': '#C60C30', 'code': 'kr'},
	'Netherlands': {'color': '#21468B', 'code': 'nl'},
	'New Zealand': {'color': '#00247D', 'code': 'nz'},
	'Norway': {'color': '#ED2939', 'code': 'no'},
	'Peru': {'color': '#D91023', 'code': 'pe'},
	'Poland': {'color': '#DC143C', 'code': 'pl'},
	'Romania': {'color': '#FCD116', 'code': 'ro'},
	'Russian Federation': {'color': '#D52B1E', 'code': 'ru'},
	'South Africa': {'color': '#006233', 'code': 'za'},
	'Spain': {'color': '#F1BF00', 'code': 'es'},
	'Sweden': {'color': '#006AA7', 'code': 'se'},
	'Switzerland': {'color': '#FF0000', 'code': 'ch'},
	'Türkiye': {'color': '#E30A17', 'code': 'tr'},
	'Ukraine': {'color': '#FFD500', 'code': 'ua'},
	'United Kingdom': {'color': '#CF142B', 'code': 'gb'},
	'United States': {'color': '#3C3B6E', 'code': 'us'},
	'Uruguay': {'color': '#0038A8', 'code': 'uy'},
	'Venezuela': {'color': '#FCD116', 'code': 've'},
}
for (country of Object.keys(countries)) {
	countries[country]['display'] = true;
}

async function fetchPage(url) {

	let items = [];
	
	if (url == dir + fname.replace('<COUNTRY>', 'Switzerland')) {  // no perm page
		return {};
	}
    
	try {
		
		const response = await fetch(url);
		const page = await response.text();
		let parser = new DOMParser();
		let htmlDoc = parser.parseFromString(page, 'text/html');
		
		//stationsDoc = htmlDoc.getElementById('ann-stations')
		stationsDoc = htmlDoc.getElementById('perm-stations')
		for (report_item of stationsDoc.getElementsByClassName('report--item')) {
			let item = {};
			for (child of report_item.children) {
				if (child.className == 'report--item__header') {
					let header = child.getElementsByClassName('row')[1].innerText.trim().split('\n');
					let NAME = header.at(0);
					let TYPE = header.at(-1).trim();
					item['NAME'] = NAME;
					item['TYPE'] = TYPE;
				}
			}
			for (child of report_item.getElementsByClassName('report--item--header--title__value fs14 fw-500')) {
				let line = child.innerText.trim().split('\n');
				if (line[0].slice(0, 10) == 'Site Name:') {
					function LatLonStr2Float(LatLonStr) {
						let L_str = LatLonStr.replace(/[^\d .]+/g, ' ').split(' ').filter(Number);
						let L = parseInt(L_str[0]);
						if (L_str.length > 1) {
							L = L + parseFloat(L_str[1]) / 60;
							if (L_str.length > 2) {
								L = L + parseFloat(L_str[2]) / (60 * 60);
							}
						}
						if (LatLonStr.includes('S') || LatLonStr.includes('W')) {
							L = L * -1;
						}
						return L;
					}
					let LAT = LatLonStr2Float(line[1])
					let LON = LatLonStr2Float(line[2])
					item['LAT'] = LAT;
					item['LON'] = LON;
				}
			}
			items.push(item);
		}
		
	return items;

	} catch (error) {
		console.error("Error:", error);
	}
}

// --------------------------------

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

async function main() {
	
	let country_data = [];
	for (country_name of Object.keys(countries)) {
		let url = dir + fname.replace('<COUNTRY>', country_name);
		let items = await fetchPage(url);
		if (Object.keys(items).length > 0) {
			let data = {'country': country_name, 'items': items}
			country_data.push(data);
		}
	}
	
	canvas.width = 1600;
	canvas.height = 1200;

	let context = d3.select('#canvas')
	.node()
	.getContext('2d');

	let projection = d3.geoOrthographic()
	.rotate([0, 90])
	.scale(canvas.height * 0.99)
	.translate([canvas.width / 2, canvas.height / 2]);

	let graticule = d3.geoGraticule();
	let geoGenerator = d3.geoPath(projection, context);
	let geoStation = d3.geoCircle();
	
	function drawMap() {

		context.beginPath();
		geoGenerator({type: 'FeatureCollection', features: land.features})
		context.fillStyle = 'white';
		context.fill();
		
		context.beginPath();
		geoGenerator({type: 'FeatureCollection', features: iceshelves.features})
		context.fillStyle = '#e8f4f8';
		context.fill();
		
		context.beginPath();
		geoGenerator(graticule());
		context.strokeStyle = 'gray';
		context.lineWidth = 2;
		context.stroke();

		for (data of country_data) {
			if (countries[data['country']]['display']) {
				context.lineWidth = 1.5;
				for (item of data['items']) {
					context.fillStyle = countries[data['country']]['color'];
					context.strokeStyle = 'white';
					if (item['TYPE'] == 'Station') {
						geoStation.radius(0.5);
					}
					else {
						geoStation.radius(0.3);
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
	
	drawMap();

	var tooltip = document.getElementById('tooltip');
	d3.select('canvas').on('mousemove', (event) => {
		const { width, height } = canvas.getBoundingClientRect();
		let mouse = projection.invert([d3.pointer(event)[0] * canvas.width / width, 
		                               d3.pointer(event)[1] * canvas.height / height]);
		let tooltipOn = false;
		for (data of country_data) {
			for (item of data['items']) {
				if (d3.geoDistance(mouse, [item['LON'], item['LAT']]) < 0.01) {
					if (countries[data['country']]['display'] == true) {
						tooltip.style.display = 'block';
						tooltip.style.left = (event.pageX + 10) + 'px';
						tooltip.style.top = (event.pageY + 10) + 'px';
						tooltip.innerHTML = item['NAME'] + '<br><i>' + item['TYPE'] + '</i><br><b>' + data['country'] + '</b>';
						tooltipOn = true;
					}
				}
			}
		}
		if (tooltipOn == false) {
			tooltip.style.display = 'none';
		}
	})
	
	let flag_height = 'calc((90vmin / ' + (Object.keys(countries).length / 2).toString() + ') - 0.5vmin)';
	let flag_width = 'calc((120vmin / ' + (Object.keys(countries).length / 2).toString() + ') - 0.5vmin)';
	var flags = document.getElementById('flags');
	flags.style.width = 'calc(2 * ' + flag_width + ' + 1.0vmin)';
	function positionFlags() {
		if (canvas.getBoundingClientRect().left > 0) {
			flags.style.right = canvas.getBoundingClientRect().left + 'px';
		}
		else {
			flags.style.right = 0;
		}
	}
	positionFlags();
	window.addEventListener('resize', function (event) {
		positionFlags();
	})
	for (country_name of Object.keys(countries)) {
		flags.innerHTML += '<img class="flag" id="flag-' + country_name + 
		                   '" src="./flags/' + countries[country_name]['code'] + '.svg"' +
						   'title="' + country_name + '"></img>';
		let flag = document.getElementById('flag-' + country_name);
		flag.style.height = flag_height;
		flag.style.width = flag_width;
		flag.style.margin = '0.25vmin';
		flag.style.objectFit = 'cover';
	}
	for (flag of document.getElementsByClassName('flag')) {
		flag.addEventListener('click', function (event) {
			let country_name = event.target.id.split('-').slice(1)[0];
			toggleCountry(country_name);
		})
	}
	function toggleCountry(country_name) {
		let flag = document.getElementById('flag-' + country_name);
		if (countries[country_name]['display'] == true) {
			countries[country_name]['display'] = false;
			flag.style.opacity = 0.6;
		}
		else if (countries[country_name]['display'] == false) {
			countries[country_name]['display'] = true;
			flag.style.opacity = 1.0;
		}
		context.clearRect(0, 0, canvas.width, canvas.height);
		drawMap();
	}

	document.getElementById('loading').remove()
}

main();
