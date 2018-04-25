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
                      zip(radicies, [BALL_SMALL, BALL_MEDIUM, BALL_LARGE])]
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
        # TODO: Scalar is undefined?
        # if (color == RED):
        #     mask = mask | cv2.inRange(hsv, Scalar(170, 70, 50), Scalar(180, 255, 255));

        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=3)
        self.mask = mask

    def update(self, image, frame_number, dispatcher):
        self._update_mask(image)
        self.frame_number = frame_number
        ''' Update locations of all balls found by mask '''
        for c in self.get_contours():
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            size = self.guess_ball_size(int(x), int(y), radius)
            self.balls[size].update_state(x, y, frame_number)
            self.balls[size].radius = radius

        ''' Reset balls that have been hanging aroud for too long '''
        # TODO: figure out a frame reset period
        for ball in self.balls:
            if (ball.current_state.frame_number):
                if (frame_number - ball.current_state.frame_number) > 3:
                    ball.reset()

                    #TODO: move logic
                    if (not ball.current_state or not ball.current_state.x):
                        event = BallOff(ball)
                        if (ball.previous_state and ball.previous_state.x):
                            print("(REAL?) NOTE OFF: ", ball.color, ball.size)
                        dispatcher.send(event)


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

    def guess_ball_size(self, x, y, radius):
        ''' Algorithm to determine what ball is being detected based on a location and a radius '''
        d_r_small, d_r_medium, d_r_large = self._get_differences_from_radius(radius)
        d_r_min = min(d_r_small, d_r_medium, d_r_large)

        radius_guess = BALL_LARGE
        if d_r_small == d_r_min:
            radius_guess = BALL_SMALL
        elif d_r_medium == d_r_min:
            radius_guess = BALL_MEDIUM

        # We won't mistake it for being the biggest one (implies r_r_large == d_r_min)
        if radius_guess == BALL_LARGE:
            return radius_guess


        point = np.array((x, y))
        d_small, d_medium, d_large = self._get_differences_from_point(point)
        d_min = min([d_small, d_medium, d_large])

        proximity_guess = BALL_LARGE
        if d_small == d_min:
            proximity_guess = BALL_SMALL
        elif d_medium == d_min:
            proximity_guess = BALL_MEDIUM

        # attempt to match radius with proximity
        # high confidence
        if proximity_guess == radius_guess:
            return proximity_guess

        # we know there is a bias for it to think the radius is smaller than it is, so we attempt to work around that
        # check that medium radius guess is not really a large ball.
        if radius_guess == BALL_MEDIUM:

            # if radius REALLY seems like its for a medium ball, let it be medium
            if d_r_medium * 2 < d_r_large:
                return BALL_MEDIUM

            # otherwise, proximity decides
            if d_large < d_medium:
                return BALL_LARGE
            return BALL_MEDIUM

        # same thing here, but for small -> medium (assume it won't actaully be large)
        if radius_guess == BALL_SMALL:
            if d_r_small * 2 < d_r_medium:
                return BALL_SMALL
            if d_2 < d_1:
                return BALL_MEDIUM
            return BALL_SMALL

        #Somehow this all fails, we return -1 so we can debug
        raise Exception("COULD NOT GUESS BALL SIZE")
