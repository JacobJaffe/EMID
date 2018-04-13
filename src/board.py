from ball import Ball
from entity import Entity
import cv2
import numpy as np


BLUE, GREEN, YELLOW, RED = 'blue', 'green', 'yellow', 'red'
COLORS = [BLUE, GREEN, YELLOW, RED]

GREEN_HSV = {'lower': (33, 50, 26), 'upper': (102, 145, 255)}
BLUE_HSV = {'lower': (103, 102, 0), 'upper': (122, 255, 255)}
RED_HSV = {'lower': (0, 0, 0), 'upper': (0, 0, 0)}
YELLOW_HSV = {'lower': (0, 0, 0), 'upper': (0, 0, 0)}

HSV = {BLUE: BLUE_HSV,
       GREEN: GREEN_HSV,
       RED: RED_HSV,
       YELLOW: YELLOW_HSV}


class Board:
    '''
    Board:
        keeps track of balls on the board and is responsible for
        detecting collisions and sending events to the dispatcher
    '''
    def __init__(self):
        self.balls = {BLUE: [], GREEN: []}
        self.entities = []
        self.sides = []
        self.masks = {BLUE: None, GREEN: None}
        self.contours = {}

    def _create_mask(image, color):
        ''' creates a mask over a image for a color '''

        ''' resize the frame, blur it, and convert it to the
            HSV color space'''
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        ''' construct a mask for the color, then perform a series
            of dilations and erosions to remove any small blobs
            left in the mask '''
        mask = cv2.inRange(hsv, color['lower'], color['upper'])
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=3)
        return mask

    def _get_contours_by_mask(image, mask):
        ''' Returns balls of a given color determined by mask '''
        return cv2.findContours(mask.copy(),
                cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    def _get_distances(self, center, color):
        ''' Shit that Jacob wrote '''

        ''' Really big default distances '''
        distances = [3649, 3649, 3649]
        return distances

    def _get_key(self, center, radius, color):
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

        d_1, d_2, d_3 = self._get_distances(center, color)
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
            if d_r2 * 2 < d_r3:
                return 2
            if d_3 < d_2:
                return 3
            return 2

        if radius_guess == 1:
            if d_r1 * 2 < d_r2:
                return 1
            if d_2 < d_1:
                return 2
            return 1

        #Somehow this all fails, we return -1 so we can debug
        return -1;

    def update(self, image):
        '''
        Tracks and finds balls.
        Updates their locations.
        Doesn't check collisions.
        Assumes that the corners of image are the corners of the board.
        '''

        ''' Construct all masks '''
        self.contours = {}
        for color in COLORS:
            mask = self._create_mask(image, HSV[color])
            self.masks[color] = mask
            contours = self._get_contours_by_mask(image, mask)
            self.contours[color] = contours
            for c in contours:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
            center = (int(x), int(y))
            key = getKey(center, radius, color)

