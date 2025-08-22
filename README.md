Built a lightweight, real-time object-distance estimator using OpenCV + NumPy (no Mediapipe) that runs on plain Python (works with DroidCam / webcam) — accurate enough for lab demos, pen-cap tests and marker-to-marker distance measurements.

Short summary
I solved a practical problem: measure distances between visible points (dots, pen caps, objects) using a single camera. Because Mediapipe wasn’t available on Python 3.13, I implemented a robust contour/blob-based pipeline with careful calibration, noise filtering and performance optimizations to make the system reliable on commodity hardware.

Problem

Need: measure distance between physical points (small dots / objects) in real time using only a single camera (phone as camera via DroidCam or laptop webcam).

Constraints: run on Python 3.13 (so no Mediapipe), limited CPU, variable lighting, tiny dots and distracting background noise.

Solution — high level

Capture video from webcam or phone (DroidCam URL).

Preprocess frames: convert to grayscale → blur → adaptive/OTSU threshold → morphological open/close to remove noise.

Detect round blobs using cv2.SimpleBlobDetector (tuned for area, circularity, convexity, inertia).

Select candidate keypoints (top by size/quality).

Compute pixel distances between centers; convert pixels → physical units (cm) using a calibration factor.

Draw bounding circles/labels, lines and distance text on the output frame.

Optimize capture size and processing frequency to keep the system real-time.

Key algorithmic decisions (why it works)

Adaptive threshold + morphological ops deals with shadows, non-uniform lighting and paper texture.

SimpleBlobDetector is faster and more stable than naive contour heuristics for round marks. Tuning minArea, minCircularity removes false positives (dust, gridlines).

Selecting top N blobs ensures the system focuses only on the points you placed (not random noise).

Calibration factor method lets you convert pixel distances to real units using a simple one-step measurement — avoids expensive stereo rigs for many classroom tasks.

Calibration (how to compute the conversion factor)

Place a reference object of known length L_cm (e.g., a ruler, 5.0 cm card) on the same plane and at the same distance from the camera as your dots.

Capture a frame and detect the two points at the ends of the reference object; measure their pixel distance d_pixels.

Compute calibration_factor = L_cm / d_pixels.

For any measured pixel distance d_px, physical distance = d_px * calibration_factor.
Note: This works well when the object plane is parallel to the camera sensor. Perspective / tilt will introduce error — see “next steps” below for correction methods.

Parameter tuning (practical tips)

params.minArea: reduce to ~15–40 for very small marks; increase to 200–2000 to ignore small noise.

params.minCircularity: set 0.7–0.85 to prefer round dots.

Adaptive threshold blockSize and C: tweak if table pattern or shadow; blockSize=51 and C=5 is a good start.

Morphological kernel: (3,3) for light smoothing; increase for heavier noise removal.

EXPECTED_POINTS (if used): set to number of dots you actually place, otherwise detect all.

Performance & robustness tips

Capture at 320×240 or 640×480 — much faster than 720/1080.

If CPU is limited: process every 2nd or 3rd frame.

Use cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320) and CAP_PROP_FRAME_HEIGHT.

For long runs consider a separate capture thread to avoid frame drops.

If you need real-time >30 FPS or heavy models, consider GPU/CUDA OpenCV builds or an edge device (Raspberry Pi + NCS or Jetson).

Example calibration snippet (concept)
d_pixels = measured_pixel_distance_between_known_points
calibration_factor = known_length_cm / d_pixels
distance_cm = measured_pixels * calibration_factor


(Use multiple calibration samples at the intended working distance and average for better stability.)

Results & observed behavior

Detects small round marks and pen caps reliably after parameter tuning.

Filtering by circularity + area removed most spurious detections (dust, glare).

System gives stable pixel→cm readings when calibration object and points are roughly co-planar.

Lag reduced significantly by downscaling frames and processing fewer frames per second.

Limitations & next steps

Perspective error: with objects at different depths or tilted planes, results will be biased. Solve with homography (if you have a planar reference) or by moving to stereo depth estimation.

Absolute accuracy: limited by camera FOV, lens distortion and calibration precision. Use lens undistortion (OpenCV camera calibration) to improve accuracy.

Occlusion / non-round objects: for complex shapes or occlusions, consider marker-based approaches (ArUco) or ML models.

Mediapipe alternative: when you switch to Python 3.10/3.11, Mediapipe/hand-landmarks can give more semantic point selection (fingers, etc.) and better tracking.

How to reproduce / try it now

Install dependencies: pip install opencv-python numpy

Use your phone with DroidCam (or webcam). Set the stream URL in the script or cap = cv2.VideoCapture(0) for local webcam.

Place a ruler/known object, run the calibration step to compute calibration_factor.

Place your points and run detection — lines and distances will be overlaid on the live video.

Call to action

If you’d like, I can:

share the polished repo (with README + calibration tool + sample images),

add an auto-calibration utility that detects a printed checkerboard and computes per-pixel scale + lens undistortion, or

convert this pipeline to run on a phone / Raspberry Pi for field testing.