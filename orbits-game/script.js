
let frame_rate = 30;
let time_step = 10;

let G = 6.67408e-11; // m3 kg-1 s-2
let unit_modifier = 5e4;  // m px-1

let player_acceleration = 5e-4 * unit_modifier;
let player_rotation = 5e0;

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
document.getElementById('player').style.transform = m2pxTransform(bodies['player'], unit_modifier);

bodies['planet']['mass'] = 6e24;
bodies['planet']['size'] = 2*6371e3;
document.getElementById('planet').style.height = Number.parseFloat(bodies['planet']['size'] / unit_modifier) + 'px';
document.getElementById('planet').style.width = Number.parseFloat(bodies['planet']['size'] / unit_modifier) + 'px';

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

const executeMoves = () => {
	
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
	
	console.log(bodies['player']['acceleration'][0], bodies['player']['acceleration'][1])
	
	document.getElementById('player').style.transform = m2pxTransform(bodies['player'], unit_modifier);

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

	let [player_x, player_y] = bodies['player']['position']
	player_x = Number.parseFloat(player_x / 1e3).toPrecision(5)//.toExponential(3)
	player_y = Number.parseFloat(player_y / 1e3).toPrecision(5)//.toExponential(3)
	document.getElementById('player-position').innerHTML = `\xa0\xa0\xa0(${player_x}, ${player_y}) km`;

}
setInterval(function(){ executeMoves() }, 1000*(1/frame_rate))
