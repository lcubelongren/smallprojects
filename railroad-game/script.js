
var board_state = {};

let subRoute = '<div class="q1"></div><div class="q2"></div><div class="q3"></div><div class="q4"></div>';
let routeDict = {
	'straight-highway': {
		'HTML': '<div class="route straight-highway">' + subRoute + '</div></div>',
		'type': { 'top': 'road', 'right': false, 'bottom': 'road', 'left': false },
	},
	'straight-railway': {
		'HTML': '<div class="route straight-railway">' + subRoute + '</div>',
		'type': { 'top': 'rail', 'right': false, 'bottom': 'rail', 'left': false },
	},
	'curved-highway': {
		'HTML': '<div class="route curved-highway">' + subRoute + '</div>',
		'type': { 'top': false, 'right': 'road', 'bottom': 'road', 'left': false },
	},
	'curved-railway': {
		'HTML': '<div class="route curved-railway">' + subRoute + '</div>',
		'type': { 'top': false, 'right': 'rail', 'bottom': 'rail', 'left': false },
	},
	't-junction-highway': {
		'HTML': '<div class="route t-junction-highway">' + subRoute + '</div>',
		'type': { 'top': false, 'right': 'road', 'bottom': 'road', 'left': 'road' },
	},
	't-junction-railway': {
		'HTML': '<div class="route t-junction-railway">' + subRoute + '</div>',
		'type': { 'top': false, 'right': 'rail', 'bottom': 'rail', 'left': 'rail' },
	},
	't-junction-station-1': {
		'HTML': '<div class="route t-junction-station-1">' + subRoute + '<div class="station"></div>',
		'type': { 'top': 'road', 'right': 'rail', 'bottom': 'road', 'left': false },
	},
	't-junction-station-2': {
		'HTML': '<div class="route t-junction-station-2">' + subRoute + '<div class="station"></div>',
		'type': { 'top': 'rail', 'right': 'road', 'bottom': 'rail', 'left': false },
	},
	'straight-station': {
		'HTML': '<div class="route straight-station">' + subRoute + '<div class="station"></div>',
		'type': { 'top': 'road', 'right': false, 'bottom': 'rail', 'left': false },
	},
	'curved-station': {
		'HTML': '<div class="route curved-station">' + subRoute + '<div class="station"></div>',
		'type': { 'top': false, 'right': 'road', 'bottom': 'rail', 'left': false },
	},
	'double-curved-highway': {
		'HTML': '<div class="route double-curved-highway">' + subRoute + '</div>',
		'type': { 'top': 'road', 'right': 'road', 'bottom': 'road', 'left': 'road' },
	},
	'double-curved-railway': {
		'HTML': '<div class="route double-curved-railway">' + subRoute + '</div>',
		'type': { 'top': 'rail', 'right': 'rail', 'bottom': 'rail', 'left': 'rail' },
	},
	'dead-end-highway': {
		'HTML': '<div class="route dead-end-highway">' + subRoute + '<div class="station"></div>',
		'type': { 'top': false, 'right': false, 'bottom': false, 'left': 'road' },
	},
	'dead-end-railway': {
		'HTML': '<div class="route dead-end-railway">' + subRoute + '<div class="station"></div>',
		'type': { 'top': false, 'right': false, 'bottom': false, 'left': 'rail' },
	},
	'overpass': {
		'HTML': '<div class="route overpass">' + subRoute + '<div class="tunnel"></div>',
		'type': { 'top': 'road', 'right': 'rail', 'bottom': 'road', 'left': 'rail' },
	},
};
var transformed_routeDict = structuredClone(routeDict);

let possible_dice = document.getElementById('possible-dice');
for (let route of Object.values(routeDict)) {
	possible_dice.innerHTML += '<button class="die">' + route['HTML'] + '</button>';
}

async function rollDice() {
	for (let rolling_die of document.getElementById('rolling-dice').children) {
		diceAnimation(rolling_die);
		let random_idx = Math.floor(Math.random() * Object.keys(routeDict).length);
		let route = Object.values(routeDict)[random_idx];
		rolling_die.innerHTML = route['HTML'];
	}
}

async function diceAnimation(die) {
	const delay = ms => new Promise(res => setTimeout(res, ms));
	die.style.border = '1.2vmin solid black';
	await delay(50);
	die.style.border = '2.4vmin solid black';
	await delay(50);
	die.style.border = '3.6vmin solid black';
	await delay(50);
	die.style.border = '3.6vmin solid black';
	await delay(50);
	die.style.border = '2.6vmin solid black';
	await delay(50);
	die.style.border = '1.2vmin solid black';
	await delay(50);
	die.style.border = '0.6vmin solid black';
}

function renderBoard() {
	
	let board = document.getElementById('board');
	
	function addExits(tile, column, row) {
		let exit = document.createElement('div');
		exit.className = 'exit';
		let line = document.createElement('hr');
		line.style.border = '0';
		if (([1, 7].includes(column) & row == 4) | ([2, 6].includes(column) & [1, 7].includes(row))) {
			line.style.borderBottom = '0.6vmin solid black';
		} else {
			line.style.borderBottom = '0.6vmin dashed black';
		}
		let arrow = document.createElement('div');
		arrow.className = 'arrow';
		if ([2, 4, 6].includes(row) & column == 1) {
			exit.style.alignSelf = 'center';
			exit.style.justifySelf = 'left';
			exit.style.transform = 'translateX(-3vmin) rotate(-90deg)';
			exit.insertAdjacentElement('beforeend', arrow);
			exit.insertAdjacentElement('beforeend', line);
			tile.insertAdjacentElement('beforeend', exit);
		}
		if ([2, 4, 6].includes(row) & column == 7) {
			exit.style.alignSelf = 'center';
			exit.style.justifySelf = 'right';
			exit.style.transform = 'translateX(3vmin) rotate(90deg)';
			exit.insertAdjacentElement('beforeend', arrow);
			exit.insertAdjacentElement('beforeend', line);
			tile.insertAdjacentElement('beforeend', exit);
		}
		if ([2, 4, 6].includes(column) & row == 1) {
			exit.style.alignSelf = 'start';
			exit.style.justifySelf = 'center';
			exit.style.transform = 'translateY(-4.25vmin) rotate(0deg)';
			exit.insertAdjacentElement('beforeend', arrow);
			exit.insertAdjacentElement('beforeend', line);
			tile.insertAdjacentElement('beforeend', exit);
		}
		if ([2, 4, 6].includes(column) & row == 7) {
			exit.style.alignSelf = 'end';
			exit.style.justifySelf = 'center';
			exit.style.transform = 'translateY(4.25vmin) rotate(180deg)';
			exit.insertAdjacentElement('beforeend', arrow);
			exit.insertAdjacentElement('beforeend', line);
			tile.insertAdjacentElement('beforeend', exit);
		}
	}

	let dimensions = [7, 7];
	board.style.gridTemplateColumns = 'repeat(' + dimensions[0] + ', minmax(0, 1fr))';
	board.style.gridTemplateRows = 'repeat(' + dimensions[1] + ', minmax(0, 1fr))';
	for (let tile_num = 0; tile_num < (dimensions[0] * dimensions[1]); tile_num++) {
		let column = (tile_num % dimensions[1]) + 1;
		let row = Math.floor(tile_num / dimensions[1]) + 1;
		let id = String(row) + '_' + String(column);
		let tile;
		if (document.getElementById(id) == null) {
			tile = document.createElement('div');
		}
		else {
			tile = document.getElementById(id);
		}
		tile.className = 'tile';
		tile.id = id;
		tile.style.gridColumn = column;
		addExits(tile, column, row);
		board.insertAdjacentElement('beforeend', tile);
	}
}

renderBoard();

function startGame() {
	for (let row = 0; row <= 8; row++) {
		for (let column = 0; column <= 8; column++) {
			board_state[row + '_' + column] = { 'top': false, 'right': false, 'bottom': false, 'left': false };
		}
	}
	board_state['0_2']['bottom'] = 'road';
	board_state['0_4']['bottom'] = 'rail';
	board_state['0_6']['bottom'] = 'road';
	board_state['2_8']['left'] = 'rail';
	board_state['4_8']['left'] = 'road';
	board_state['6_8']['left'] = 'rail';
	board_state['8_6']['top'] = 'road';
	board_state['8_4']['top'] = 'rail';
	board_state['8_2']['top'] = 'road';
	board_state['6_0']['right'] = 'rail';
	board_state['4_0']['right'] = 'road';
	board_state['2_0']['right'] = 'rail';
	document.getElementById('start-game').remove();
	document.getElementById('controls').style.visibility = 'visible';
	newRound();
}

function newRound() {
	let transformed_routeDict = structuredClone(routeDict);
	for (let i = 0; i < 4; i++) {
		let die = document.createElement('button');
		die.className = 'die';
		die.setAttribute('onclick', 'highlightRoutes(event)');
		document.getElementById('rolling-dice').insertAdjacentElement('beforeend', die);
	}
	rollDice();
}

function highlightRoutes(event) {
	let selected_route = event.target.className.split(' ')[1];
	findPossible(selected_route, highlight=false);
	if (Object.values(event.target.classList).includes('highlight-possible')) {
		event.target.classList.remove('highlight-possible');
	} else {
		for (let route_die of document.getElementsByClassName('route')) {
			route_die.classList.remove('highlight-possible');
		}
		event.target.classList.add('highlight-possible');
		findPossible(selected_route, highlight=true);
	}
}

function findPossible(route, highlight) {
	for (let tile of document.getElementsByClassName('tile')) {
		if (highlight == true) {
			if (!tile.classList.contains('filled')) {
				let neighbor_top = (parseInt(tile.id.split('_')[0]) - 1) + '_' + parseInt(tile.id.split('_')[1]);
				let neighbor_right = parseInt(tile.id.split('_')[0]) + '_' + (parseInt(tile.id.split('_')[1]) + 1);
				let neighbor_bottom = (parseInt(tile.id.split('_')[0]) + 1) + '_' + parseInt(tile.id.split('_')[1]);
				let neighbor_left = parseInt(tile.id.split('_')[0]) + '_' + (parseInt(tile.id.split('_')[1]) - 1);
				if (transformed_routeDict[route]['type']['top'] != false) {
					if (!Object.values(board_state[neighbor_top]).every((x) => x == false)) {
						if (board_state[neighbor_top]['bottom'] == transformed_routeDict[route]['type']['top']) {
							tile.classList.add('highlight-possible');
							tile.setAttribute('onclick', 'placeRoute(event)');
						}
					}
				}
				if (transformed_routeDict[route]['type']['right'] != false) {
					if (!Object.values(board_state[neighbor_right]).every((x) => x == false)) {
						if (board_state[neighbor_right]['left'] == transformed_routeDict[route]['type']['right']) {
							tile.classList.add('highlight-possible');
							tile.setAttribute('onclick', 'placeRoute(event)');
						}
					}
				}
				if (transformed_routeDict[route]['type']['bottom'] != false) {
					if (!Object.values(board_state[neighbor_bottom]).every((x) => x == false)) {
						if (board_state[neighbor_bottom]['top'] == transformed_routeDict[route]['type']['bottom']) {
							tile.classList.add('highlight-possible');
							tile.setAttribute('onclick', 'placeRoute(event)');
						}
					}
				}
				if (transformed_routeDict[route]['type']['left'] != false) {
					if (!Object.values(board_state[neighbor_left]).every((x) => x == false)) {
						if (board_state[neighbor_left]['right'] == transformed_routeDict[route]['type']['left']) {
							tile.classList.add('highlight-possible');
							tile.setAttribute('onclick', 'placeRoute(event)');
						}
					}
				}
			}
		} else {
			tile.classList.remove('highlight-possible');
			tile.removeAttribute('onclick');
		}
	}
}

function placeRoute(event) {
	let selected_route;
	let selected_rotation;
	let selected_transform;
	for (let selected of document.getElementsByClassName('highlight-possible')) {
		if (Object.values(selected.classList).includes('route')) {
			selected_route = selected.classList[1];
			selected_rotation = parseInt(selected.parentElement.style.rotate.split('deg')[0]);
			if (selected.parentElement.style.transform == '') {
				selected_transform = '1';
			} else {
				selected_transform = parseInt(selected.parentElement.style.transform.split('scale(')[1].split(',')[0]);
			}
			selected.parentElement.remove();
		}
	}
	let tile = event.target;
	tile.innerHTML += transformed_routeDict[selected_route]['HTML'];
	for (let child of tile.children) {
		if (Object.values(child.classList).includes('route')) {
			child.style.rotate = selected_rotation + 'deg';
			child.style.transform = 'scale(' + selected_transform + ', 1)';
		}
	}
	tile.classList.add('filled');
	board_state[tile.id] = transformed_routeDict[selected_route]['type'];
	findPossible('', highlight=false);
	if (document.getElementById('rolling-dice').children.length == 0) {
		newRound();
	}
}

function controlDice(action) {
	let modified = [];
	for (let rolling_die of document.getElementById('rolling-dice').children) {
		let route = rolling_die.children[0].classList[1];
		transformed_routeDict_route = structuredClone(transformed_routeDict[route]);
		let current_rotation = parseInt(rolling_die.style.rotate.split('deg')[0]);
		if (isNaN(current_rotation)) {
			current_rotation = 0;
		}
		if (action == 'rotate-left') {
			rolling_die.style.rotate = current_rotation - 90 + 'deg';
			if (!modified.includes(route)) {
				transformed_routeDict[route]['type']['top'] = transformed_routeDict_route['type']['right'];
				transformed_routeDict[route]['type']['right'] = transformed_routeDict_route['type']['bottom'];
				transformed_routeDict[route]['type']['bottom'] = transformed_routeDict_route['type']['left'];
				transformed_routeDict[route]['type']['left'] = transformed_routeDict_route['type']['top'];
			}
		}
		if (action == 'rotate-right') {
			rolling_die.style.rotate = current_rotation + 90 + 'deg';
			if (!modified.includes(route)) {
				transformed_routeDict[route]['type']['top'] = transformed_routeDict_route['type']['left'];
				transformed_routeDict[route]['type']['right'] = transformed_routeDict_route['type']['top'];
				transformed_routeDict[route]['type']['bottom'] = transformed_routeDict_route['type']['right'];
				transformed_routeDict[route]['type']['left'] = transformed_routeDict_route['type']['bottom'];
			}
		}
		if (action == 'mirror-axis') {
			let current_transform = rolling_die.style.transform;
			if (current_transform == '') {
				rolling_die.style.transform = 'scale(-1, 1)';
			} else {
				let new_scaleX = parseInt(current_transform.split('scale(')[1].split(',')[0]) * -1;
				rolling_die.style.transform = 'scale(' + new_scaleX + ', 1)';
			}
			if (!modified.includes(route)) {
				transformed_routeDict[route]['type']['right'] = transformed_routeDict_route['type']['left'];
				transformed_routeDict[route]['type']['left'] = transformed_routeDict_route['type']['right'];
			}
		}
		modified.push(route);
	}
}
