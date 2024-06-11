
let frame_rate = 60;
let time_step = 10;

let G = 6.67408e-11; // m3 kg-1 s-2
let unit_modifier = 5e4;  // m px-1

let player_acceleration = 2e-4 * unit_modifier;
let player_rotation = 3e0;

// Helper function to convert units while getting transform.
// Everything is in [m] besides the .style.transform, which is [px].
function m2pxTransform(body, unit_modifier) {
	let x = body['position'][0] / unit_modifier;
	let y = body['position'][1] / unit_modifier;
	let r = body['rotation'];
	let transform_str = `translate(${x}px, ${y}px) rotate(${r}deg)`;
	return transform_str;
}

let body_names = ['player', 'planet'];
let bodies = {}
for (name of body_names) {
	bodies[name] = { position: [0, 0], velocity: [0, 0], acceleration: [0, 0], mass: 1, rotation: null, size: null };
}

bodies['player']['position'] = [0, -(418e3+6371e3)];
bodies['player']['velocity'] = [7.67e3, 0];
bodies['player']['mass'] = 4.5e5;
bodies['player']['rotation'] = 90;
bodies['player']['size'] = 25;

bodies['planet']['mass'] = 6e24;
bodies['planet']['size'] = 2*6371e3;

document.documentElement.style.setProperty('--player-size', Number.parseFloat(bodies['player']['size']) + 'px');
document.getElementById('planet').style.height = Number.parseFloat(bodies['planet']['size'] / unit_modifier) + 'px';
document.getElementById('planet').style.width = Number.parseFloat(bodies['planet']['size'] / unit_modifier) + 'px';

// Add stars to the background.
let star_num = 100;
let background = document.getElementById('background');
for (let i = 0; i < star_num; i++) {
	let [star_x, star_y, star_r] = [Math.random() * 100, Math.random() * 100, Math.random() * 0];
	let star_transform = `transform: translate(${star_x}vw, ${star_y}vh) rotate(${star_r}deg);`;
	let star_duration = Math.random() * (3 - 2) + 2;
	let star_animation = `animation: star ${star_duration}s linear infinite;`;
	background.innerHTML += `<div class='star' style='${star_transform} ${star_animation}'></div>`;
}

const controller = {
	'ArrowUp': {pressed: false},
	'ArrowLeft': {pressed: false},
	'ArrowRight': {pressed: false},
}

controller['ArrowUp']['func'] = function() {
	dax = player_acceleration * Math.sin(bodies['player']['rotation'] * Math.PI / 180);
	day = -player_acceleration * Math.cos(bodies['player']['rotation'] * Math.PI / 180);
	dr = 0;
	return [dax, day, dr]
}
controller['ArrowLeft']['func'] = function() {
	dax = 0;
	day = 0;
	dr = -player_rotation;
	return [dax, day, dr]
}
controller['ArrowRight']['func'] = function() {
	dax = 0;
	day = 0;
	dr = player_rotation;
	return [dax, day, dr]
}

document.addEventListener('keydown', (e) => {
  if(controller[e.key]){
    controller[e.key].pressed = true;
	
  }
})
document.addEventListener('keyup', (e) => {
  if(controller[e.key]){
    controller[e.key].pressed = false;
  }
})

let view_modifier = 1;

const executeMoves = () => {
	
	// Move the player with engines and gravity.
	bodies['player']['acceleration'] = [0, 0];
	Object.keys(controller).forEach(key => {
		if (controller[key].pressed) {
			[dax, day, dr] = controller[key].func()
			bodies['player']['acceleration'][0] += dax;
			bodies['player']['acceleration'][1] += day;		
			bodies['player']['rotation'] += dr;
		}
	})
	bodies = Gravity(bodies, time_step, G);  // from ./motion.js
	document.getElementById('player').style.transform = m2pxTransform(bodies['player'], unit_modifier);

	// Show and hide the fire animations.
	document.getElementById('player-fire-down').style.visibility = 'hidden';
	document.getElementById('player-fire-left').style.visibility = 'hidden';
	document.getElementById('player-fire-right').style.visibility = 'hidden';
	if (controller['ArrowUp']['pressed']) {
		document.getElementById('player-fire-down').style.visibility = 'visible';
	}
	if (controller['ArrowLeft']['pressed']) {
		document.getElementById('player-fire-right').style.visibility = 'visible';
	}
	if (controller['ArrowRight']['pressed']) {
		document.getElementById('player-fire-left').style.visibility = 'visible';
	}

	// Write the player position at the bottom of the window.
	let [player_x, player_y] = bodies['player']['position'];
	player_x_km = Number.parseFloat(+player_x / 1e3).toPrecision(4);
	player_y_km = Number.parseFloat(-player_y / 1e3).toPrecision(4);
	document.getElementById('player-position').innerHTML = `\xa0\xa0\xa0(${player_x_km} x, ${player_y_km} y) km`;
	
	// Move the viewport in and out as the player moves.
	let view_min = 2*6371e3;  // m
	let view_max = 6*6371e3;  // m
	if ((Math.abs(player_x) > view_max) || (Math.abs(player_y) > view_max)) {
	}
	else if ((Math.abs(player_x) > view_min) || (Math.abs(player_y) > view_min)) {
		view_modifier = Math.max(Math.abs(player_x), Math.abs(player_y)) / view_min;
		view_modifier = 1 + Math.log(view_modifier**3)
	}
	else {
		view_modifier = 1;
	}
	unit_modifier = 5e4 * view_modifier;
	document.documentElement.style.setProperty('--player-size', Number.parseFloat(bodies['player']['size'] / view_modifier) + 'px');
	document.getElementById('planet').style.height = Number.parseFloat(bodies['planet']['size'] / (unit_modifier * view_modifier)) + 'px';
	document.getElementById('planet').style.width = Number.parseFloat(bodies['planet']['size'] / (unit_modifier * view_modifier)) + 'px';
	
}
setInterval(function(){ executeMoves() }, 1000*(1/frame_rate))
