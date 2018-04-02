from camera import Camera
import cv2
import numpy as np

# import the necessary packages
from collections import deque
import argparse
import imutils
import sys

greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

redLower = (244, 0, 0)
redUpper = (255, 130, 130)
# 64 frames
BUFFER = 32
pts = deque(maxlen=BUFFER)

cam = Camera(int(sys.argv[1]))
while(True):
    frame, warp = cam.get_frame_and_warp()

    # get heights and widths for each image
    frame_h, frame_w = frame.shape[:2]

    # blank copy
    frame_projection = np.zeros((600, 600, 3), np.uint8)

    # fill blank with warp
    if warp is not None:
        warp_h, warp_w = warp.shape[:2]
        # resize warp to fill the window
        if warp_h > warp_w:
            warp = imutils.resize(warp, height=frame_h)
        else:
            warp = imutils.resize(warp, width=frame_w)
        frame_projection[0:0+warp.shape[0], 0:0+warp.shape[1]] = warp

	# resize the frame, blur it, and convert it to the HSV
	# color space
	# blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame_projection, cv2.COLOR_BGR2HSV)


    cv2.imshow('Camera', frame)
    cv2.imshow('Projection', frame_projection)
    cv2.imshow('hsv', hsv)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cam.close()

cv2.destroyAllWindows()
