
let player_x = 0;
let player_y = 0;
let player_r = 0;
let [dx, dy, dr] = [0, 0, 0];

let player_speed = 10;
let frame_rate = 30;

let g = frame_rate * 0.0005;

const controller = {
	"ArrowUp": {pressed: false},
	"ArrowLeft": {pressed: false},
	"ArrowRight": {pressed: false},
}

controller["ArrowUp"]["func"] = function() {
	dx = player_speed * Math.sin(player_r * Math.PI / 180);
	dy = -player_speed * Math.cos(player_r * Math.PI / 180);
	dr = 0;
	return [dx, dy, dr]
}
controller["ArrowLeft"]["func"] = function() {
	dx = 0;
	dy = 0;
	dr = -player_speed * 0.5;
	return [dx, dy, dr]
}
controller["ArrowRight"]["func"] = function() {
	dx = 0;
	dy = 0;
	dr = player_speed * 0.5;
	return [dx, dy, dr]
}

document.addEventListener("keydown", (e) => {
  if(controller[e.key]){
    controller[e.key].pressed = true;
	
  }
})
document.addEventListener("keyup", (e) => {
  if(controller[e.key]){
    controller[e.key].pressed = false;
  }
})

const executeMoves = () => {
	Object.keys(controller).forEach(key => {
		if (controller[key].pressed) {
			[dx, dy, dr] = controller[key].func()
			player_x += dx;
			player_y += dy;
			player_r += dr;
		}
	})
	
	function Gravity(g, center=[0, 0]) {
		let [x0, y0] = center;
		dx = g * (x0 - player_x)
		dy = g * (y0 - player_y);
		dr = 0;
		return [dx, dy, dr];
	}

	[dx, dy, dr] = Gravity(g);
	player_x += dx;
	player_y += dy;
	player_r += dr;
	
	player.style.transform = "translate(" + player_x + "px," + player_y + "px) rotate(" + player_r + "deg)";
	
	document.getElementById("player-fire-down").style.visibility = "hidden";
	document.getElementById("player-fire-left").style.visibility = "hidden";
	document.getElementById("player-fire-right").style.visibility = "hidden";
	if (controller["ArrowUp"]["pressed"]) {
		document.getElementById("player-fire-down").style.visibility = "visible";
	}
	if (controller["ArrowLeft"]["pressed"]) {
		document.getElementById("player-fire-right").style.visibility = "visible";
	}
	if (controller["ArrowRight"]["pressed"]) {
		document.getElementById("player-fire-left").style.visibility = "visible";
	}
}
setInterval(function(){ executeMoves() }, 1000*(1/frame_rate))
