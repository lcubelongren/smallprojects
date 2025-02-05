
let track = [];

window.onload = function() {
	rollDice();
	document.getElementById('hint').style.visibility = 'visible';
}

const delay = ms => new Promise(res => setTimeout(res, ms));

async function rollDice() {
	let combined = 0;
	for (let die of document.getElementsByClassName('die')) {
		let num = parseInt(Math.floor(Math.random() * 6) + 1);
		combined += num;
		diceAnimation(die, num);
	}
	track.push(combined);
	updateHistogram(combined);
	updatePlot();
	document.getElementById('hint').style.visibility = 'hidden';
}

async function diceAnimation(die, num) {
	die.innerText = '';
	die.style.border = '15px solid black';
	await delay(50);
	die.style.border = '25px solid black';
	await delay(50);
	die.style.border = '35px solid black';
	await delay(50);
	die.style.border = '35px solid black';
	await delay(50);
	die.style.border = '25px solid black';
	await delay(50);
	die.style.border = '15px solid black';
	await delay(50);
	die.style.border = '10px solid black';
	die.innerText = num;
}

function updateHistogram(num) {
	let bar = document.getElementById('bar-' + num);
	let current_size = window.getComputedStyle(bar).borderBottomWidth.split('px')[0];
	bar.style.borderBottomWidth = parseInt(current_size) + 10 + 'px';
}

function updatePlot() {
	function Gaussian(x) {
		let mean = 0;
		for (let x of track) {
			mean += x / track.length;
		}
		let sigma = 0;
		for (let x of track) {
			sigma += (x - mean) ** 2;
		}
		if (!sigma == 0) {
			sigma = Math.sqrt((1 / track.length) * sigma);
			return (1 / (sigma * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * (x - mean) ** 2 / sigma ** 2);
		}
	}
	let canvas = document.getElementById('plot');
	canvas.height = window.innerHeight;
	canvas.width = window.innerWidth;
	let ctx = canvas.getContext('2d');
	ctx.beginPath();
	ctx.strokeStyle = 'black';
	ctx.lineWidth = 3;
	ctx.shadowColor = 'white';
	ctx.shadowOffsetY = 3;
	let starting_height = 40;
	let lines = 48;
	for (let i=0; i <= lines; i++) {
		let dice_value = ((12 - 2) * i / lines) + 2;
		let y_point = canvas.height - starting_height - (Gaussian(dice_value) * canvas.height * 2);
		let x_point = canvas.width * i / lines;
		ctx.lineTo(x_point, y_point);
		ctx.stroke();
	}
}
