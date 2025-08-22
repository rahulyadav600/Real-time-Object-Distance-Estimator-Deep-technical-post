import cv2
import numpy as np
import math as m

URL = "http://10.87.74.158:4747/video"
distance_threshold = 0.06912

cap = cv2.VideoCapture(URL)

params = cv2.SimpleBlobDetector_Params()
params.filterByColor = True
params.blobColor = 255
params.minThreshold = 10
params.maxThreshold = 255
params.thresholdStep = 10
params.filterByArea = True
params.minArea = 30
params.maxArea = 5000
params.filterByCircularity = True
params.minCircularity = 0.70
params.filterByInertia = True
params.minInertiaRatio = 0.2
params.filterByConvexity = True
params.minConvexity = 0.7

detector = cv2.SimpleBlobDetector_create(params)

while True:
    ok, frame = cap.read()
    if not ok:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bin_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV, 51, 5)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, k, iterations=1)
    bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, k, iterations=1)

    keypoints = detector.detect(bin_img)
    keypoints = sorted(keypoints, key=lambda kp: kp.size, reverse=True)

    centers = []
    out = frame.copy()
    for i, kp in enumerate(keypoints):
        x, y = int(kp.pt[0]), int(kp.pt[1])
        r = max(4, int(kp.size / 2))
        centers.append((x, y))
        cv2.circle(out, (x, y), r, (0, 255, 0), 2)
        cv2.circle(out, (x, y), 4, (0, 0, 255), -1)
        cv2.putText(out, chr(65 + i), (x + 6, y - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    for i in range(len(centers)):
        for j in range(i + 1, len(centers)):
            (x1, y1), (x2, y2) = centers[i], centers[j]
            dpx = m.hypot(x2 - x1, y2 - y1)
            dcm = dpx * distance_threshold
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            cv2.line(out, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(out, f"{dcm:.2f} cm", (mx, my),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imshow("final output", out)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
