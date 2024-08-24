
//https://www.ats.aq/devAS/InformationExchange/ArchivedInformation

let dir = './reports/2022_2023/';
let fname = 'Annual report - 2022_2023 - Report - <COUNTRY>.html';
let colors = {  // https://vexillogasm.com/country-flags/
	'Argentina': '#74ACDF',
	'Australia': '#00008B',
	'Belgium': '#FCD116',
	'Brazil': '#009B3A',
	'Bulgaria': '#00966E',
	'Canada': '#FF0000',
	'Chile': '#0039A6',
	'China': '#DE2910',
	'Czechia': '#11457E',
	'Finland': '#003580',
	'France': '#002395',
	'Germany': '#FFCE00',
	'India': '#FF9933',
	'Italy': '#009246',
	'Japan': '#BC002D',
	'Korea (ROK)': '#C60C30',
	'New Zealand': '#00247D',
	'Norway': '#ED2939',
	'Poland': '#DC143C',
	'Russian Federation': '#D52B1E',
	'Spain': '#F1BF00',
	'Sweden': '#006AA7',
	'Switzerland': '#FF0000',
	'Türkiye': '#E30A17',
	'Ukraine': '#FFD500',
	'United Kingdom': '#CF142B',
	'United States': '#3C3B6E',
	'Uruguay': '#0038A8',
};

async function fetchPage(url) {

	let items = [];
    
	try {
		
		const response = await fetch(url);
		const page = await response.text();
		let parser = new DOMParser();
		let htmlDoc = parser.parseFromString(page, 'text/html');
		
		stationsDoc = htmlDoc.getElementById('ann-stations')
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
	console.log(items)
	return items;

	} catch (error) {
		console.error("Error:", error);
	}
}

// --------------------------------

async function main() {
	
	let country_data = [];
	for (country_name of Object.keys(colors)) {
		let url = dir + fname.replace('<COUNTRY>', country_name);
		let items = await fetchPage(url);
		let data = {'country': country_name, 'items': items}
		country_data.push(data);
	}

	let geojson_url = 'https://cdn.jsdelivr.net/npm/world-atlas@2/land-50m.json'

	let geojson = {}

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

	function update() {

		context.clearRect(0, 0, canvas.width, canvas.height);

		context.beginPath();
		geoGenerator({type: 'FeatureCollection', features: geojson.features})
		context.fillStyle = 'white';
		context.fill();

		context.beginPath();
		geoGenerator(graticule());
		context.strokeStyle = 'white';
		context.lineWidth = 2;
		context.stroke();
		
		for (data of country_data) {
			context.lineWidth = 1;
			for (item of data['items']) {
				context.fillStyle = colors[data['country']];
				context.strokeStyle = colors[data['country']];
				if (item['TYPE'] == 'Station') {
					geoStation.radius(0.5);
				}
				else {
					geoStation.radius(0.25);
				}
				geoStation.center([item['LON'], item['LAT']]);
				context.beginPath();
				geoGenerator(geoStation());
				context.fill();
				context.stroke();
			}
		}
		
		//d3.selectAll("canvas").on("mousemove", (event) => 
		//console.log(projection.invert([d3.pointer(event)[0] * 1.59, d3.pointer(event)[1] * 1.59])))
		
	}

	d3.json(geojson_url)
	.then(function(data) {
		geojson = topojson.feature(data, data.objects.land);
		window.setInterval(update, 100);
	})
	
	

}

main();
