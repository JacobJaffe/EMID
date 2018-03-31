from camera import Camera
import cv2
import numpy as np

cam = Camera(1)
while True:
    frame, warp = cam.get_frame_and_warp()
    h, w = frame.shape[:2]
    frame_projection = np.zeros((h, w, 3), np.uint8)
    if warp is not None:
        frame_projection[0:0+warp.shape[0], 0:0+warp.shape[1]] = warp

    cv2.imshow('Camera', frame)
    cv2.imshow('Projection', frame_projection)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cam.close()

cv2.destroyAllWindows()
