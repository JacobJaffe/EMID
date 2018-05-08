from constants import *
import cv2
import numpy as np

'''
    Defines how to create a mask for a specific color.
    Some masks are better with certain dialations, iterations, hsv combinations,
    etc., so it's easier to just make specific functions for each.
'''

def red_mask(image):
        '''convert it to HSV color space'''
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        ''' select by color '''
        mask_1 = cv2.inRange(hsv, (0, 150, 150), (5, 255, 255))

        # NOTE: the 120 value of saturation lower might need adjusting!
        mask_2 = cv2.inRange(hsv, (170, 120, 150), (180, 255, 255))

        ''' combine masks '''
        mask = mask_1 | mask_2

        ''' remove small blobs, then fill in gaps '''
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=3)

        return mask

# TODO: ensure this works! Probably is overshooting rn!
def blue_mask(image):
            '''convert it to HSV color space'''
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            ''' select by color '''
            mask = cv2.inRange(hsv, (102, 60, 72), (119, 255, 255))

            ''' remove small blobs, then fill in gaps '''
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=3)

            return mask

# TODO: ensure this works! Probably is overshooting rn!
def green_mask(image):
            '''convert it to HSV color space'''
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            ''' select by color '''
            mask = cv2.inRange(hsv, (65,60,60), (90,255,255))

            ''' remove small blobs, then fill in gaps '''
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=3)

            return mask

# TODO: ensure this works! Probably is overshooting rn!
def yellow_mask(image):
            '''convert it to HSV color space'''
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            ''' select by color '''
            mask = cv2.inRange(hsv, (15, 60, 180), (30, 180, 255))

            ''' remove small blobs, then fill in gaps '''
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=3)

            return mask

def orange_mask(image):
            '''convert it to HSV color space'''
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            ''' select by color '''
            mask = cv2.inRange(hsv, (4, 97, 200), (12, 180, 255))

            ''' remove small blobs, then fill in gaps '''
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=3)

            return mask

def maroon_mask(image):
            '''convert it to HSV color space'''
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            ''' select by color '''
            mask = cv2.inRange(hsv, (158, 65, 50), (184, 188, 182))

            ''' remove small blobs, then fill in gaps '''
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=3)

            return mask

MASK_CONSTRUCTORS = {BLUE: blue_mask,
        GREEN: green_mask,
        RED: red_mask,
        YELLOW: yellow_mask,
        ORANGE: orange_mask,
        MAROON: maroon_mask}
