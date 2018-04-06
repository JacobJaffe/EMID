from camera import Camera
import cv2
import numpy as np
import sys
from pythonosc import udp_client

# import the necessary packages
from collections import deque
import argparse
import imutils
import sys

PORT = 3649
CHANNEL = 1
X_MAX = 600.0
Y_MAX = 600.0
yellow = {'lower': (5,40,245), 'upper': (44,74,255)}
#           (H_min, S_min, V_min)      (H_max, S_max, V_max)
green = {'lower': (29, 86, 6), 'upper': (64, 255, 255)}
red = {'lower': (0, 126, 53), 'upper': (4, 255, 255)}
blue = {'lower': (103,102,0), 'upper': (113,255,255)}
color = blue

# 64 frames
BUFFER = 32


# def write_warp(warp, projection):
#     if warp is not None:
#         warp_h, warp_w = warp.shape[:2]
#         # resize warp to fill the window
#         if warp_h > warp_w:
#             warp = imutils.resize(warp, height=frame_h)
#         else:
#             warp = imutils.resize(warp, width=frame_w)
#         projection[0:0+warp.shape[0], 0:0+warp.shape[1]] = warp
#         return warp, projection


def get_mask(projection, color):
    # resize the frame, blur it, and convert it to the HSV
    # color space
    # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(projection, cv2.COLOR_BGR2HSV)

    # construct a mask for the color, then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, color['lower'], color['upper'])
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=3)
    return mask


pts = deque(maxlen=BUFFER)
client = udp_client.SimpleUDPClient('127.0.0.1', PORT)
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

    mask = get_mask(frame_projection, color)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
	   cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    i = 1
    # only proceed if at least one contour was found
    for c in cnts:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        # c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        
        # send OSC message to Max
        # Make sure y is inverted in value when jsending messages
        client.send_message('/{0}/{1}'.format(CHANNEL, i), [x/X_MAX*100., (1-(y/Y_MAX))*100., 64])
        
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        # draw the circle and centroid on the frame,
        # then update the list of tracked points
        cv2.circle(frame_projection, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
        cv2.circle(frame_projection, center, 5, (0, 0, 255), -1)

        # update the points queue
        pts.appendleft(center)
        i += 1

    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(BUFFER / float(i + 1)) * 2.5)
        cv2.line(frame_projection, pts[i - 1], pts[i], (0, 0, 255), thickness)


    cv2.imshow('Camera', frame)
    cv2.imshow('Projection', frame_projection)
    cv2.imshow('Mask', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cam.close()

cv2.destroyAllWindows()
