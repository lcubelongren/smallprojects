
// Make the background grid.
let cellNum = 100;
for (let i = 0; i < cellNum; i++) {
	let child = document.createElement("div");
	child.className = "tile";
	child.id = i;
	document.getElementById("background").appendChild(child);
}

// Define a random number generation function.
function getRandomInt(min, max, num) {
	//const minCeiled = Math.ceil(min);
	//const maxFloored = Math.floor(max);
	//return Math.floor(Math.random() * (maxFloored - minCeiled) + minCeiled);
	let idxs = [];
	for (let i = min; i < max; i++) {
		idxs.push(i);
	}
	function shuffle(o) {
		for(var j, x, i = o.length; i; j = parseInt(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
    return o;
	}
	return shuffle(idxs).slice(0, num);
}

// Start the game by choosing goal tiles.
var points = 0;
var chosenNum = 30;
let tileIdxs = getRandomInt(0, cellNum, chosenNum);
for (idx of tileIdxs) {
	document.getElementById(idx).className = "tile-goal";
}

// Make the points counter.
//document.getElementById("counter").innerHTML = points + " / " + chosenNum;

// Make a loop that constantly changes board state.
var n1 = setInterval(function() {
	let idx = tileIdxs[getRandomInt(0, chosenNum, 1)[0]];
	let currentTile = document.getElementById(idx).className;
	if (currentTile == "tile-goal") {
		document.getElementById(idx).className = "tile-changing";
	}
}, 500);
// Only keep changing and avoid tiles for a set time.
var n2 = setInterval(function() {
	for (idx of tileIdxs) {
		let currentTile = document.getElementById(idx).className;
		if (currentTile == "tile-changing") {
			document.getElementById(idx).className = "tile-avoid";
		}
	}
}, 2000);
var n3 = setInterval(function() {
	for (idx of tileIdxs) {
		let currentTile = document.getElementById(idx).className;
		if (currentTile == "tile-avoid" && !getRandomInt(0, 5, 1)[0]) {
			document.getElementById(idx).className = "tile-goal";
		}
	}
}, 3000);

// Get the mouse pointer value.
// On hover over grid, change tile colors.
// While hovering, check for the following:
// if goal tile, gain a point,
// but if an avoid tile, the player loses.
function playerLost() {
	for (let i = 0; i < cellNum; i++) {
		let tile = document.getElementById(i);
		//tile.removeEventListener(type, listener)
		tile.className = "tile-lost";
	}
	document.getElementById("reload").style.visibility = "visible";
	document.getElementById("counter").innerHTML = points + " / " + chosenNum;
}
for (let i = 0; i < cellNum; i++) {
	let tile = document.getElementById(i);
	tile.addEventListener('mouseenter', enter => {
		let startingClass = enter.target.className;
		if (startingClass == "tile") {
		}
		if (startingClass == "tile-goal" || startingClass == "tile-changing") {
			points += 1;
			document.getElementById("counter").innerHTML = points + " / " + chosenNum;
		}
		if (startingClass == "tile-touched") {
			playerLost();
		}
		else if (startingClass == "tile-avoid") {
			playerLost();
		}
		else {
			enter.target.className = "tile-touched";
		}
	}, {passive: true})
}
