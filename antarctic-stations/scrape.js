
// Run by itself with node.

//https://www.ats.aq/devAS/InformationExchange/ArchivedInformation
//https://www.ats.aq/devAS/InformationExchange/LatestReports

//let dir = './reports/2022_2023/';
//let fname = 'Annual report - 2022_2023 - Report - <COUNTRY>.html';
let dir = './reports/Permanent_information/';  // no relative pathing with node
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

async function fetchPage(url) {

	let items = [];
	
	if (url == dir + fname.replace('<COUNTRY>', 'Switzerland')) {  // no perm page
		return {};
	}
    
	const response = await fetch(url);
	const page = await response.text();
	let parser = new DOMParser();
	let htmlDoc = parser.parseFromString(page, 'text/html');
	
	function LatLonStr2Float(LatLonStr) {
		let L_str = LatLonStr.replace(/[^\d.]+/g, ' ').trim().split(' ');
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
	
	//stationsDoc = htmlDoc.getElementById('ann-stations');
	stationsDoc = htmlDoc.getElementById('perm-stations');
	for (report_item of stationsDoc.getElementsByClassName('report--item')) {
		let item = {};
		for (child of report_item.children) {
			if (child.className == 'report--item__header') {
				let row = child.getElementsByClassName('row');
				let header = row[1].innerText.trim().split('\n');
				item['NAME'] = header.at(0);
				item['TYPE'] = header.at(-1).trim();
			}
		}
		for (child of report_item.getElementsByClassName('report--item--header--title__value fs14 fw-500')) {
			let line = child.innerText.trim().split('\n');
			if (line[0].slice(0, 10) == 'Site Name:') {
				item['LAT'] = LatLonStr2Float(line[1]);
				item['LON'] = LatLonStr2Float(line[2]);
			}
		}
		items.push(item);
	}
	
	arsDoc = htmlDoc.getElementById('perm-ars');
	for (report_item of arsDoc.getElementsByClassName('report--item')) {
		let item = {};
		for (child of report_item.children) {
			if (child.className == 'report--item__header') {
				for (child of report_item.getElementsByClassName('report--item--header--title__value fs14 fw-500')) {
					let row = child.innerHTML.split('</span>');
					if (row[0].split('<strong>')[1] == 'Site Name</strong>: ') {
						item['NAME'] = row[1].split('&nbsp;&nbsp;-')[0];
						item['TYPE'] = 'Automatic Recording Station';
						item['LAT'] = LatLonStr2Float(row[2].split('&nbsp;&nbsp;-')[0]);
						item['LON'] = LatLonStr2Float(row[3].split('&nbsp;&nbsp;-')[0]);
					}
				}
			}
		}
		items.push(item)
	}

	// https://stackoverflow.com/a/58437069
	let unique_items = items.filter((v, i, a) => a.findIndex(v2 => (JSON.stringify(v) === JSON.stringify(v2))) === i)
	return unique_items;

}

async function run() {
	let country_data = [];
	for (country_name of Object.keys(countries)) {
		let url = dir + fname.replace('<COUNTRY>', country_name);
		console.log(url)
		let items = await fetchPage(url);
		let data = {};
		data[country_name] = { 
			'items': items, 
			'color': countries[country_name]['color'],
			'code': countries[country_name]['code'],
		}
		country_data.push(data);
	}
	return country_data;
}

async function main() {
	let data = await run();
	console.log('Saving .json file...')
	var bb = new Blob([JSON.stringify(data)], { type: 'json' });
	var a = document.createElement('a');
	a.download = 'scrape_data.json';
	a.href = window.URL.createObjectURL(bb);
	a.click();
}

main();
