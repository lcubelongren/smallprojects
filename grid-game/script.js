
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
var chosenNum = 50;
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
		if (currentTile == "tile-avoid" && !getRandomInt(0, 10, 1)[0]) {
			document.getElementById(idx).className = "tile-goal";
		}
	}
}, 3000);

// Get the mouse hover value.
// On hover over grid, change tile colors.
// While hovering, check for the following:
// if goal tile, gain a point,
// but if an avoid tile, the player loses.
document.addEventListener('mousemove', e => {
	//console.clear()
	let target = document.elementFromPoint(e.clientX, e.clientY);
	if (target.classList.contains("tile")) {
		target.className = "tile-touched";
	}
	if (target.classList.contains("tile-goal") || target.classList.contains("tile-changing")) {
		target.className = "tile-touched";
		points += 1;
		document.getElementById("counter").innerHTML = points + " / " + chosenNum;
	}
	if (target.classList.contains("tile-avoid")) {
		clearInterval(n1);
		clearInterval(n2);
		clearInterval(n3);
		for (let i = 0; i < cellNum; i++) {
			let currentTile = document.getElementById(i).className;
			document.getElementById(i).className = "tile-lost";
		}
		document.getElementById("button").style.visibility = "visible";
		document.getElementById("counter").innerHTML = points + " / " + chosenNum;
	}
}, {passive: true})
