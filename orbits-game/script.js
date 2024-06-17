
// hide until page is loaded
document.body.style.visibility = 'hidden';  
document.getElementById('background').style.visibility = 'visible';
document.getElementById('loadingscreen').style.visibility = 'visible';

let G = 6.67408e-11;  // m3 kg-1 s-2
let unit_modifier = 5e4;  // m px-1
let view_modifier = 1;

let frame_rate = 60;  // frames s-1
let time_step = 10;  // s frame-1

let player_acceleration = 1e-1 * unit_modifier / (time_step * frame_rate);
let player_rotation = 2e2 / frame_rate;

// Helper function to convert units while getting transform.
// Everything is in [m] besides the .style.transform, which is [px].
function m2pxTransform(body, unit_modifier) {
	let x = body['position'][0] / unit_modifier;
	let y = body['position'][1] / unit_modifier;
	let r = body['rotation'];
	let transform_str = `translate(${x}px, ${y}px) rotate(${r}deg)`;
	return transform_str;
}

let body_names = ['player', 'planet', 'station'];
let bodies = {}
for (name of body_names) {
	bodies[name] = { position: [0, 0], velocity: [0, 0], acceleration: [0, 0], mass: 1, rotation: null, size: null };
}

let player_tile = '0,0';
let tile_info = {
	 '0,0': { planet_color: ['green',     'blue'], planet_mass: 6e24, planet_size: 2*6371e3, station_size: 30 },  // Earth
	'-1,0': { planet_color: ['orange',    'grey'], planet_mass: 6e23, planet_size: 2*3390e3, station_size:  0 },  // Mars
	 '1,0': { planet_color: ['brown',     'blue'], planet_mass: 2e27, planet_size: 2*6991e4, station_size:  0 },  // Jupiter
	'0,-1': { planet_color: ['lightgrey', 'grey'], planet_mass: 3e23, planet_size: 2*2440e3, station_size:  0 },  // Mercury
	 '0,1': { planet_color: ['white',     'grey'], planet_mass: 5e24, planet_size: 2*6052e3, station_size:  0 },  // Venus
}

bodies['player']['position'] = [0, -(23222e3+6371e3)];
bodies['player']['velocity'] = [3.68e3, 0];
bodies['player']['mass'] = 675;
bodies['player']['rotation'] = 90;
bodies['player']['size'] = 50;

bodies['planet']['mass'] = 6e24;
bodies['planet']['size'] = 2*6371e3;

bodies['station']['position'] = [0, ((422e3+413e3)/2+6371e3)];
bodies['station']['velocity'] = [7.67e3, 0];
bodies['station']['mass'] = 4.5e5;
bodies['station']['rotation'] = 0;
bodies['station']['size'] = 30;

document.documentElement.style.setProperty('--player-size', Number.parseFloat(bodies['player']['size']) + 'px');
document.documentElement.style.setProperty('--station-size', Number.parseFloat(bodies['station']['size']) + 'px');
document.documentElement.style.setProperty('--planet-color', 'linear-gradient(green, blue)');

document.getElementById('planet').style.height = Number.parseFloat(bodies['planet']['size'] / unit_modifier) + 'px';
document.getElementById('planet').style.width = Number.parseFloat(bodies['planet']['size'] / unit_modifier) + 'px';

// Add stars to the background.
let star_num = 100;
let background = document.getElementById('background');
for (let i = 0; i < star_num; i++) {
	let [star_x, star_y, star_r] = [Math.random() * 88 + 1, Math.random() * 88 + 1, Math.random() * 0];  // for 5vmin/5vmax body border
	let star_transform = `transform: translate(${star_x}vw, ${star_y}vh) rotate(${star_r}deg);`;
	background.innerHTML += `<div class='star' style='${star_transform}'></div>`;
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

let loading_screen = true;

const executeMoves = () => {
	
	Object.keys(controller).forEach(key => {
		if (controller[key].pressed) {
			loading_screen = false;
			document.body.style.visibility = 'visible';
			document.getElementById('loadingscreen').style.visibility = 'hidden';
		}
	})
	if (loading_screen) {
		return null;
	}
	
	let orbit_period;
	// Rotate planet on its axis.
	orbit_period = 24 * 60;  // minutes
	bodies['planet']['rotation'] -= (360 / (60 * orbit_period)) * time_step;
	// Rotate station along orbit.
	orbit_period = 92.9 - 0.7;  // minutes
	bodies['station']['rotation'] -= (360 / (60 * orbit_period)) * time_step;
	if ((Math.abs(bodies['planet']['position'][0] - bodies['station']['position'][0]) < 1e5) &&
		((bodies['planet']['position'][1] - bodies['station']['position'][1]) < 0)) {
		bodies['station']['rotation'] = 0;  // reset at the centerline
	}
	
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
	for (target_name in bodies) {
		document.getElementById(target_name).style.transform = m2pxTransform(bodies[target_name], unit_modifier);
	}

	// Show and hide the fire animations.
	if (controller['ArrowUp']['pressed']) {
		document.getElementById('player-fire-down').style.visibility = 'visible';
	}
	else {
		document.getElementById('player-fire-down').style.visibility = 'hidden';
	}
	if (controller['ArrowLeft']['pressed']) {
		document.getElementById('player-fire-right').style.visibility = 'visible';
	}
	else {
		document.getElementById('player-fire-right').style.visibility = 'hidden';
	}
	if (controller['ArrowRight']['pressed']) {
		document.getElementById('player-fire-left').style.visibility = 'visible';
	}
	else {
		document.getElementById('player-fire-left').style.visibility = 'hidden';
	}

	// Write the player position at the bottom of the window.
	let [player_x, player_y] = bodies['player']['position'];
	player_x_km = Number.parseFloat(+player_x / 1e3).toPrecision(4);
	player_y_km = Number.parseFloat(-player_y / 1e3).toPrecision(4);
	document.getElementById('player-position').innerHTML = `tile (${player_tile}) - (${player_x_km} x, ${player_y_km} y) km`;
	
	// Move the viewport in and out as the player moves.
	let view_min = 2*6371e3;  // m
	let view_max = 6*6371e3;  // m
	let view_modifier_max = 1 + Math.log((view_max / view_min)**3);
	let player2planet_distance = Math.abs(Math.sqrt(player_x**2 + player_y**2));
	if (bodies['planet']['mass'] > 0) {
		if (player2planet_distance > view_max) {
		}
		else if (player2planet_distance > view_min) {
			view_modifier = 1 + Math.log((player2planet_distance / view_min)**3)
		}
		else {
			view_modifier = 1;
		}
	}
	unit_modifier = 5e4 * view_modifier;
	document.documentElement.style.setProperty('--player-size', Number.parseFloat(bodies['player']['size'] / view_modifier) + 'px');
	document.documentElement.style.setProperty('--station-size', Number.parseFloat(bodies['station']['size'] / view_modifier) + 'px');
	document.getElementById('planet').style.height = Number.parseFloat(bodies['planet']['size'] / (unit_modifier)) + 'px';
	document.getElementById('planet').style.width = Number.parseFloat(bodies['planet']['size'] / (unit_modifier)) + 'px';
	document.getElementById('background').style.transform = `scale(${view_modifier_max/view_modifier})`;
	
	// Move between tiles.
	tile_transition = false;
	tile = player_tile.split(',');
	let background_bounds = document.getElementById('background').getBoundingClientRect();
	let height = background_bounds.height;
	let width = background_bounds.width;
	if ((2 * (player_y / unit_modifier) + height) < 0) {
		tile_transition = true;
		player_tile = tile[0] + ',' + (parseInt(tile[1]) + 1);
		bodies['player']['position'][1] += height * unit_modifier;
	}
	if ((2 * (player_y / unit_modifier) - height) > 0) {
		tile_transition = true;
		player_tile = tile[0] + ',' + (parseInt(tile[1]) - 1);
		bodies['player']['position'][1] -= height * unit_modifier;
	}
	if ((2 * (player_x / unit_modifier) + width) < 0) {
		tile_transition = true;
		player_tile = (parseInt(tile[0]) - 1) + ',' + tile[1];
		bodies['player']['position'][0] += width * unit_modifier;
	}
	if ((2 * (player_x / unit_modifier) - width) > 0) {
		tile_transition = true;
		player_tile = (parseInt(tile[0]) + 1) + ',' + tile[1];
		bodies['player']['position'][0] -= width * unit_modifier;
	}
	if (tile_transition) {
		if (Object.keys(tile_info).includes(player_tile)) {
			if (player_tile == '0,0') {
				bodies['station']['position'] = [0, ((422e3+413e3)/2+6371e3)];
				bodies['station']['velocity'] = [7.67e3, 0];
				bodies['station']['mass'] = 4.5e5;
				bodies['station']['rotation'] = 0;
				bodies['station']['size'] = 30;
			}
			else {
				bodies['station']['size'] = tile_info[player_tile]['station_size'];			
			}
			bodies['planet']['mass'] = tile_info[player_tile]['planet_mass'];
			bodies['planet']['size'] = tile_info[player_tile]['planet_size'];
			let [color1, color2] = tile_info[player_tile]['planet_color'];
			document.documentElement.style.setProperty('--planet-color', `linear-gradient(${color1}, ${color2})`);
		}
		else {
			bodies['planet']['mass'] = 0;
			bodies['planet']['size'] = 0;
		}
		document.documentElement.style.setProperty('--station-size', Number.parseFloat(bodies['station']['size'] / view_modifier) + 'px');
	}

}
setInterval(function(){ executeMoves() }, 1000*(1/frame_rate))
