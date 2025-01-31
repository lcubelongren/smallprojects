
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
	updateHistogram(combined);
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
	if (String(num).length == 1) {
		num = '0' + num;
	}
	let bar = document.getElementById('bar-' + num);
	let current_size = window.getComputedStyle(bar).borderBottomWidth.split('px')[0];
	bar.style.borderBottomWidth = parseInt(current_size) + 10 + 'px';
}
