import cv2
import numpy as np

cap = cv2.VideoCapture("diamond.mp4")

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

new_width = 1350
new_height = 450

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(
    "diamond_detected.mp4",
    fourcc,
    fps,
    (new_width, new_height)
)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.resize(frame, (new_width, new_height))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(
        gray, 40, 255, cv2.THRESH_BINARY
    )

    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(
        thresh, cv2.MORPH_CLOSE, kernel
    )

    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:
        area = cv2.contourArea(contour)

        if area > 10:
            x, y, w, h = cv2.boundingRect(contour)

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

    out.write(frame)

cap.release()
out.release()

print("Detection completed!")