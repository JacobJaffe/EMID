# Import packages
from camera import Camera
import cv2
import numpy as np
import sys
from pythonosc import udp_client, osc_message_builder
from collections import deque
import argparse
import imutils

# TODO: assign by COLOR
CHANNEL = 1

# This port means 'EMID'
PORT = 3649

# Known Limits of the Board
X_MAX = 600.0
Y_MAX = 500.0

# For scaling the projection
PROJECTION_SIZE = [800, 800]

# Limits for masks: (H_min, S_min, V_min)      (H_max, S_max, V_max)
GREEN_LIMITS = {'lower': (29, 86, 6), 'upper': (64, 255, 255)}
BLUE_LIMITS = {'lower': (103,102,0), 'upper': (122,255,255)}

# 64 frames
BUFFER = 32

# Map of states of balls by ID, where ID is determined by radius
BALLS = {'blue': {1: None, 2: None, 3: None}, 'green': {1: None, 2: None, 3: None}}


def getDistances(center, color):
    distances = [3649, 3649, 3649]
    for key in BALLS[color]:
        b = BALLS[color][key]
        if b:
            b_center = b['center']
            dx = np.abs(b_center[0] - center[0])
            dy = np.abs(b_center[1] - center[1])
            d = np.power(dx, 2) + np.power(dy, 2)
            d = np.sqrt(d)

            # off by one error of 1 2 3 -> 0 1 2
            distances[key - 1]  = d
    return distances

# TODO: for this to be really acurate, need to know the speed of the ball
# guess by location
def getKey(center, radius, color):

    # guess by radius
    d_r1, d_r2, d_r3 = np.abs(radius-7.), np.abs(radius-14.), np.abs(radius-20.)
    d_r_min = min([d_r1, d_r2, d_r3])

    radius_guess = 3
    if d_r1 == d_r_min:
        radius_guess = 1
    elif d_r2 == d_r_min:
        radius_guess = 2

    # We won't mistake it for being the biggest one
    if radius_guess == 3:
        return radius_guess

    d_1, d_2, d_3 = getDistances(center, color)
    d_min = min([d_1, d_2, d_3])

    proximity_guess = 3
    if d_1 == d_min:
        proximity_guess = 1
    elif d_2 == d_min:
        proximity_guess = 2

    # attempt to match radius with proximity
    # high confidence
    if proximity_guess == radius_guess:
        return proximity_guess

    # we know there is a bias for it to think the radius is smaller than it is, so we attempt to work around that
    # check that radius of 2 is not really 3
    if radius_guess == 2:
        if d_3 < d_2:
            return 3
        return 2

    if radius_guess == 1:
        if d_2 < d_1:
            return 2
        return 1




def getMask(projection, color):
    # resize the frame, blur it, and convert it to the HSV color space
    hsv = cv2.cvtColor(projection, cv2.COLOR_BGR2HSV)

    # construct a mask for the color, then perform a series of dilations and
    # erosions to remove any small blobs left in the mask
    mask = cv2.inRange(hsv, color['lower'], color['upper'])
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=3)
    return mask

def drawContours(img):
        # draw circles on the projection and on the mask
        for color in BALLS:
            for key in BALLS[color]:
                b = BALLS[color][key]
                if not b or b['last_frame'] != frame_number:
                    continue
                r = int(b['radius'])
                c = b['center']
                key = b['key']
                cv2.circle(img, c, r, (0, 255, 255), 2)
                cv2.circle(img, c, 5, (0, 0, 255), -1)
                cv2.putText(img, color + ' ' + str(key), (c[0] + 5 + r, c[1] + 5 + r), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return img

# Set up our udp client for sending to Max
client = udp_client.SimpleUDPClient('127.0.0.1', PORT)

# Set up our Camera based on the command line argument
cam = Camera(int(sys.argv[1]))

frame_number = 0
while(True):
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

    blue_mask = getMask(frame_projection, BLUE_LIMITS)
    green_mask = getMask(frame_projection, GREEN_LIMITS)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts_blue = cv2.findContours(blue_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnts_green = cv2.findContours(green_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnts_by_color = [{'color': 'blue', 'cnts': cnts_blue}, {'color': 'green', 'cnts': cnts_green}]

    center = None

    for cnts in cnts_by_color:
        color = cnts['color']
        for c in cnts['cnts']:
            # From contour, compute the center and radius
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            center = (int(x), int(y))
            key = getKey(center, radius, color)

            if BALLS[color][key]:
                cur = center
                dx, dy = cur[0]-BALLS[color][key]['center'][0], cur[1]-BALLS[color][key]['center'][1]
                dxdt, dydt = dx/2., dy/2.
                velocity = np.abs(dydt)
                client.send_message('/{0}'.format(CHANNEL), [key] + [x/X_MAX*100., (1-(y/Y_MAX))*100., velocity])
            BALLS[color][key] = {'center': center, 'radius': radius, 'key': key, 'last_frame' : frame_number}

    # Draw the stuff
    # convert to RGB, combine masks to show by color
    blue_mask = cv2.cvtColor(blue_mask, cv2.COLOR_GRAY2RGB)
    green_mask = cv2.cvtColor(green_mask, cv2.COLOR_GRAY2RGB)
    blue_mask[np.where((blue_mask == [255,255,255]).all(axis = 2))] = [255,0,0]
    green_mask[np.where((green_mask == [255,255,255]).all(axis = 2))] = [0,255,0]
    mask = blue_mask + green_mask

    frame_projection = drawContours(frame_projection)

    cv2.imshow('Camera', frame)
    cv2.imshow('Projection', frame_projection)
    cv2.imshow('mask', mask)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cam.close()

cv2.destroyAllWindows()
