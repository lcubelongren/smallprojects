
let image_uploader = document.getElementById('image-uploader');
let image_toggle = document.getElementById('image-toggle');
let board_photo = document.getElementById('board-photo');
let processing_canvas = document.getElementById('processing-canvas');

image_uploader.addEventListener('change', () => {
	board_photo.src = URL.createObjectURL(image_uploader.files[0]);
	board_photo.onload = function() {
		processImage();
		board_photo.onload = function() {};
	};
})

image_toggle.addEventListener('click', () => {
	if (board_photo.style.display == 'none') {
		board_photo.style.display = 'inherit';
		processing_canvas.style.display = 'none';
	} else {
		processing_canvas.style.display = 'inherit';
		board_photo.style.display = 'none';
	}
})

function processImage() {
	console.log('processing...')

	let src = cv.imread(board_photo);

	//cv.cvtColor(src, src, cv.COLOR_RGBA2GRAY, 0);
	//let gray = new cv.Mat();
	//cv.threshold(src, gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU);

	let dst = new cv.Mat();

	// Convert to grayscale
	cv.cvtColor(src, dst, cv.COLOR_RGBA2GRAY);

	// Apply Gaussian blur to reduce noise
	cv.GaussianBlur(dst, dst, new cv.Size(5, 5), 0, 0, cv.BORDER_DEFAULT);
	
	let edges = new cv.Mat();
	cv.Canny(dst, edges, 100, 200);
	
	// Find contours
	let contours = new cv.MatVector();
	let hierarchy = new cv.Mat();
	cv.findContours(edges, contours, hierarchy, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE);
	
	let X_points = [];
	let Y_points = [];

	// Loop through the contours to detect squares
	for (let i = 0; i < contours.size(); i++) {
		let contour = contours.get(i);

		// Approximate the contour to a polygon
		let approx = new cv.Mat();
		cv.approxPolyDP(contour, approx, 0.02 * cv.arcLength(contour, true), true);
		
		// Get (x, y) points of this contour
		for (let j = 0; j < approx.rows; j++) {
			let point = approx.data32S.slice(j * 2, (j + 1) * 2); // Get x, y for each point
			X_points.push(point[0]);
			Y_points.push(point[1]);
		}

			// Draw the square (or the detected Scrabble tile grid)
			let color = new cv.Scalar(0, 255, 0); // Green color
			cv.drawContours(src, contours, i, color, 2, cv.LINE_8, hierarchy, 0);
	
		approx.delete();
	}
	
	cv.imshow(processing_canvas, src);
	
	let aspectRatio = board_photo.naturalWidth / board_photo.naturalHeight;
	processing_canvas.style.aspectRatio = aspectRatio;

}
