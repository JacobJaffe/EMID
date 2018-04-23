# Import packages
from camera import Camera
import cv2
import numpy as np
import sys
from dispatcher import Dispatcher
from collections import deque
import argparse
import imutils
from board import Board
from exposure import *

auto_exposure_off()
exposure_range = get_range(EXPOSURE)

def set_exposure(x):
    set_value(EXPOSURE, x)

DEFAULT_EXPOSURE = exposure_range[0]

set_exposure(DEFAULT_EXPOSURE)

# This port means 'EMID'
PORT = 3649

PROJECTION_SIZE = [600, 600]

# Set up our udp client for sending to Max
dispatcher = Dispatcher(port=PORT)

# Set up our Camera based on the command line argument
cam = Camera(int(sys.argv[1]))
board = Board()
global should_update

should_update = False

def set_update_true():
    should_update = True

frame_number = 0
cv2.namedWindow("Trackbars", 0)
cv2.createTrackbar("Exposure", "Trackbars",
                   exposure_range[0],
                   exposure_range[1], set_update_true)

last_exposure = DEFAULT_EXPOSURE
while(True):
    cur_exposure = cv2.getTrackbarPos('Exposure','Trackbars')
    if cur_exposure == last_exposure and should_update:
        should_update = False
    last_exposure = cur_exposure

    #cam.set_exposure(exposure)
    frame_number = frame_number + 1

    # get frame from camera
    frame, warp = cam.get_frame_and_warp()

    # get heights and widths for each image
    frame_h, frame_w = frame.shape[:2]

    # blank copy
    frame_projection = np.zeros((PROJECTION_SIZE[0], PROJECTION_SIZE[1], 3), np.uint8)

    # fill blank with warp
    if warp is not None:
        warp_h, warp_w = warp.shape[:2]
        # resize warp to fill the window
        if warp_h > warp_w:
            warp = imutils.resize(warp, height=frame_h)
        else:
            warp = imutils.resize(warp, width=frame_w)
        frame_projection[0:0+warp.shape[0], 0:0+warp.shape[1]] = warp

    board.update(frame_projection, frame_number)
    board.send_events(dispatcher)

    mask, drawn_img = board.display(True, True)
    cv2.imshow("Mask", mask)
    cv2.imshow("Warp", drawn_img)
    cv2.imshow("Image", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cam.close()

cv2.destroyAllWindows()
