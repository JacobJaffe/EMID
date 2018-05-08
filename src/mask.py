from constants import *
import cv2
import numpy as np
from ball import Ball
from events import *

class Mask(object):
    ''' Mask:
            Defines a mask for a given color. Used for detecting balls of that
            color. Ball tracking is done at this level, as it makes for fewer
            errors.
    '''
    def __init__(self, color):
        self.color = color
        self.hsv = HSV[color]
        self.image = None
        radicies = RADICIES.copy()
        self.radicies = radicies
        self.balls = [Ball(color, radius, size)
                      for radius, size in
                      zip(radicies, [BALL_LARGE])]
        self.frame_number = 0

    def _update_mask(self, image):
        ''' creates a mask over a image for a color '''

        ''' resize the frame, blur it, and convert it to the
            HSV color space'''
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        ''' construct a mask for the color, then perform a series
            of dilations and erosions to remove any small blobs
            left in the mask '''
        mask = cv2.inRange(hsv, self.hsv['lower'], self.hsv['upper'])
        if (self.color == RED):
            mask_wrap = cv2.inRange(hsv, (170, 70, 50), (180, 255, 255))
            mask = mask | mask_wrap

        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=3)
        self.mask = mask

    def update(self, image, frame_number):
        self._update_mask(image)
        self.frame_number = frame_number
        ''' Update locations of all balls found by mask '''

        # of form ((x, y), radius)
        detected_circles = list(map(cv2.minEnclosingCircle, self.get_contours()))
        self._update_balls(detected_circles, frame_number)

    def get_contours(self):
        ''' Returns balls of a given color determined by mask '''
        return cv2.findContours(self.mask.copy(),
                cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    def get_bgr(self):
        ''' Converts mask to bgr color space and returns it '''
        # do not be fooled, it is for magical reasons going to really be in BGR
        bgr_mask = cv2.cvtColor(self.mask, cv2.COLOR_GRAY2RGB)
        bgr_mask[np.where((bgr_mask == [255,255,255]).all(axis = 2))] = BGR[self.color]
        return bgr_mask

    ''' Private methods from former BallGroup class '''
    def _get_differences_from_radius(self, radius):
        ''' Determines differencnes in the radius of balls '''
        radius_differences = [[np.abs(radius-self.radicies[0])], [np.abs(radius-self.radicies[1])], [np.abs(radius-self.radicies[2])]]
        return radius_differences

    def _get_differences_from_point(self, point):
        ''' Get distances from point for each ballself.
            Assumes point to by an numpy array of form [x, y]
        '''
        distances = [3649]*3
        for i in range(len(distances)):
            ball_location = self.balls[i].get_location()
            if (not ball_location[0]) or (not ball_location[1]):
                continue
            distances[i] = np.linalg.norm(ball_location - point)
        return distances

    # for now, only assume one ball
    def _update_balls(self, detected_circles, frame_number):

        # filter out small circles
        filtered_circles = list(filter(lambda params:
                                            params[1] > 0.5*self.radicies[0]
                                       , detected_circles))

        # sort the circles
        sorted_circles = sorted(filtered_circles, key=lambda x: x[1], reverse=True)

        if not sorted_circles:
            return

        best_circle = None
        # if ball is on the board, then match by radius AND location
        if (self.balls[0].current_state and self.balls[0].current_state.x):
            (prev_x, prev_y) = self.balls[0].current_state.get_location()

            closest_distance = np.infty
            for c in sorted_circles:
                location, check_radius = c
                distance_from_last_location = self.balls[0]._distance_from_point(location)
                if distance_from_last_location < closest_distance:
                    closest_distance = distance_from_last_location
                    best_circle = c


        # if no current state, then we only check based on radius
        else:
            # sorted_circles is in descending order!
            best_circle = sorted_circles[0]

        if best_circle is None:
            print("NO CIRCLE DETECTED")
            return

        # only largest ball, so 0
        (x, y), radius = best_circle;
        self.balls[0].update_state(x, y, frame_number)
        self.balls[0].radius = radius
