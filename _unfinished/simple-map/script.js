
async function main() {
	
	async function loadData() {

		let land_path = './maps/land-110m.json';  // topojson
		let land_data;
		await d3.json(land_path)
		.then(function(data) {
			land_data = topojson.feature(data, data.objects.land);
		})
		
		let coastline_path = './maps/ne_110m_coastline.json';  // geojson
		let coastline_data;
		await d3.json(coastline_path)
		.then(function(data) {
			coastline_data = data;
		})
		
		let ocean_path = './maps/ne_110m_ocean.json';  // geojson
		let ocean_data;
		await d3.json(ocean_path)
		.then(function(data) {
			ocean_data = data;
		})
		
		let lake_path = './maps/ne_110m_lakes.json';  // geojson
		let lake_data;
		await d3.json(lake_path)
		.then(function(data) {
			lake_data = data;
		})
		
		let river_path = './maps/ne_110m_rivers_lake_centerlines.json';  // geojson
		let river_data;
		await d3.json(river_path)
		.then(function(data) {
			river_data = data;
		})
		
		let glacier_path = './maps/ne_110m_glaciated_areas.json';  // geojson
		let glacier_data;
		await d3.json(glacier_path)
		.then(function(data) {
			glacier_data = data;
		})
		
		let iceshelf_path = './maps/ne_50m_antarctic_ice_shelves_polys.json';  // geojson
		let iceshelf_data;
		await d3.json(iceshelf_path)
		.then(function(data) {
			iceshelf_data = data;
		})

		return [land_data, coastline_data, ocean_data, lake_data, river_data, glacier_data, iceshelf_data];

	}
	
	let [land_data, coastline_data, ocean_data, lake_data, river_data, glacier_data, iceshelf_data] = await loadData();

	const canvas = document.getElementById('canvas');
	const context = canvas.getContext('2d');
	
	canvas.width = window.innerWidth;
	canvas.height = window.innerHeight;
	
	let scale = canvas.height * 0.35;
	
	let projection = d3.geoEquirectangular()
	.rotate([0, 0])
	.scale(scale)
	.translate([canvas.width / 2, canvas.height / 2]);
	
	window.addEventListener('resize', function (event) {
		canvas.width = window.innerWidth;
		canvas.height = window.innerHeight;
		projection.scale(scale);
		projection.translate([canvas.width / 2, canvas.height / 2]);
		drawMap();
	});
	window.addEventListener('wheel', function (event) {
		let cursor_timeout = setTimeout(function() { canvas.style.cursor = 'grab'; }, 100);
		if (event.deltaY < -5) {
			canvas.style.cursor = 'zoom-in';
			clearTimeout(cursor_timeout);
		}
		else if (event.deltaY > 5) {
			canvas.style.cursor = 'zoom-out';
			clearTimeout(cursor_timeout);
		}
		scale *= 1 + (-0.0005 * event.deltaY);
		scale = limit_scale(scale);
		projection.scale(scale);
		drawMap();
	});
	canvas.addEventListener('mousedown', function (event) {
		canvas.style.cursor = 'grabbing';
	});
	
	//https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events/Pinch_zoom_gestures
	const evCache = [];
	let prevDiff = -1;
	canvas.addEventListener('pointerdown', function (event) {
		evCache.push(event);
	});
	canvas.addEventListener('pointermove', function (event) {
		const index = evCache.findIndex(
			(cachedEv) => cachedEv.pointerId === event.pointerId,
		);
		evCache[index] = event;
		console.log(index, evCache.length, evCache)
		if (evCache.length === 2) {
			const XDiff = Math.abs(evCache[0].clientX - evCache[1].clientX);
			const YDiff = Math.abs(evCache[0].clientY - evCache[1].clientY);
			const curDiff = Math.abs(XDiff - YDiff);
			if (prevDiff > 0) {
				if (curDiff > prevDiff) {
					scale *= 1 + 0.005;
				}
				if (curDiff < prevDiff) {
					scale *= 1 - 0.005;
				}
				scale = limit_scale(scale);
				projection.scale(scale);
			}
			prevDiff = curDiff;
		}
	});
	canvas.addEventListener('pointerup', function (event) {
		removeEvent(event);
	});
	canvas.addEventListener('pointercancel', function (event) {
		removeEvent(event);
	});
	canvas.addEventListener('pointerout', function (event) {
		removeEvent(event);
	});
	canvas.addEventListener('pointerleave', function (event) {
		removeEvent(event);
	});
	function removeEvent(event) {
		const index = evCache.findIndex(
			(cachedEv) => cachedEv.pointerId === event.pointerId,
		);
		evCache.splice(index, 1);
		if (evCache.length < 2) {
			prevDiff = -1;
		}
	};
	
	function limit_scale(scale) {
		if (scale < canvas.height * 0.35) {
			scale = canvas.height * 0.35;
			canvas.style.cursor = 'grab';
		}
		else if (scale > canvas.height * 2.0) {
			scale = canvas.height * 2.0;
			canvas.style.cursor = 'grab';
		}
		return scale;
	};
	
	d3.select(context.canvas)
	.call(drag(projection)
	    .on('drag.render', () => { drawMap() })
		.on('end.render', () => { drawMap(); canvas.style.cursor = 'grab';})
	);
	
	const path = d3.geoPath(projection, context);
	const graticule = d3.geoGraticule()
	.extent([[-180, -90], [180, 90]])
	.step([30, 30]);
	
	function drawMap() {

		context.clearRect(0, 0, canvas.width, canvas.height);
		var style = getComputedStyle(document.body);
		context.beginPath(), path(land_data), context.fillStyle = style.getPropertyValue('--land-color'), context.fill();
		//context.beginPath(), path(ocean_data), context.fillStyle = '#a9a9a9', context.fill();
		context.beginPath(), path(lake_data), context.fillStyle = style.getPropertyValue('--water-color'), context.fill();
		context.beginPath(), path(river_data), context.strokeStyle = style.getPropertyValue('--water-color'), context.stroke();
		context.beginPath(), path(glacier_data), context.fillStyle = 'white', context.fill();
		context.beginPath(), path(iceshelf_data), context.fillStyle = '#e8f4f8', context.fill();
		context.beginPath(), path(coastline_data), context.strokeStyle = 'black', context.stroke();
		context.beginPath(), path(graticule()), context.strokeStyle = 'gray', context.stroke();
		
		getLocation();
	
	}
	
	drawMap();
	
	//https://www.w3schools.com/js/js_api_geolocation.asp
	const dot = d3.geoCircle();
	function getLocation() {
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(updatePosition);
		} else {
		}
		return
	}
	function updatePosition(position) {
		var [lat, lon] = [position.coords.latitude, position.coords.longitude];
		dot.center([lon, lat]);
		dot.radius(1500 / (scale * (Math.PI * 2)));
		context.beginPath(), path(dot()), context.fillStyle = 'tomato', context.fill();
	}

}

main();

//https://observablehq.com/d/569d101dd5bd332b
function drag(projection) {
  let v0, q0, r0;
  
  function dragstarted({x, y}) {
    v0 = versor.cartesian(projection.invert([x, y]));
    q0 = versor(r0 = projection.rotate());
  }
  
  function dragged({x, y}) {
	const v1 = versor.cartesian(projection.rotate(r0).invert([x, y]));
    const q1 = versor.multiply(q0, versor.delta(v0, v1));
    projection.rotate(versor.rotation(q1));
	//projection.rotate(versor.rotation(q1).slice(0, 2));
  }
  
  return d3.drag()
	.on("start", dragstarted)
	.on("drag", dragged);
}
