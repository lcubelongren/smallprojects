
// Make the background grid.
let cellnum = 100;
for (let i = 0; i < cellnum; i++) {
	let child = document.createElement("div");
	child.className = "tile";
	document.getElementById("background").appendChild(child);
}

// Get the mouse hover value.
// On hover over grid, change tile colors.
document.addEventListener('mousemove', e => {
	console.clear()
	let target = document.elementFromPoint(e.clientX, e.clientY);
	if (target.classList.contains("tile")) {
		target.className = "tile-touched";
	}
}, {passive: true})
