
// Calculate the forces of gravity in two dimensions.

function Gravity(bodies, time_step, G) {
	
	function calculate_single_body_acceleration(bodies, target_name) {
		let target_body = bodies[target_name];
		let acceleration = [target_body['acceleration'][0], target_body['acceleration'][1]];  // (copy)
		let external_names = Object.keys(bodies).filter((key) => { if (key != target_name) { return bodies[key] } });
		for (external_name of external_names) {
			let external_body = bodies[external_name];
			let r = (target_body.position[0] - external_body.position[0])**2 +  // x
			        (target_body.position[1] - external_body.position[1])**2;   // y
			r = Math.sqrt(r);
			let tmp = G * external_body.mass / r**3;
			acceleration[0] += tmp * (external_body.position[0] - target_body.position[0]);  // x
			acceleration[1] += tmp * (external_body.position[1] - target_body.position[1]);  // y
		}
		return acceleration;
	}
	
	function update_state(bodies, time_step) {
		for (target_name in bodies) {
			let acceleration = calculate_single_body_acceleration(bodies, target_name);
			let target_body = bodies[target_name];
			target_body.velocity[0] += acceleration[0] * time_step;  // x
			target_body.velocity[1] += acceleration[1] * time_step;  // y
			target_body.position[0] += target_body.velocity[0] * time_step;  // x
			target_body.position[1] += target_body.velocity[1] * time_step;  // y
		}
	}
	
	update_state(bodies, time_step)
	return bodies;

}
