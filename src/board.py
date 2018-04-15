from ball import Ball, BallGroup
from entity import Entity
import cv2
import numpy as np


BLUE, GREEN, YELLOW, RED = 'blue', 'green', 'yellow', 'red'
COLORS = [BLUE, GREEN, RED] # TODO: , YELLOW, RED]
RADICIES = [7., 14., 20.]

DISPLAY_SIZE = [600, 600]

GREEN_HSV = {'lower': (65,60,60), 'upper': (80,255,255)}
BLUE_HSV = {'lower': (103, 102, 0), 'upper': (122, 255, 255)}
RED_HSV = {'lower': (0, 70, 50), 'upper': (10, 255, 255)}
YELLOW_HSV = {'lower': (0, 0, 0), 'upper': (0, 0, 0)}

BLUE_BGR = (255, 0, 0)
GREEN_BGR = (0, 255, 0)
YELLOW_BGR = (0, 255, 255)
RED_BGR = (0, 0, 255)

BGR = {BLUE: BLUE_BGR,
        GREEN: GREEN_BGR,
        RED: RED_BGR,
        YELLOW: YELLOW_BGR}

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
        self.ball_groups = {
            BLUE: BallGroup(BLUE, RADICIES),
            GREEN: BallGroup(GREEN, RADICIES),
            RED: BallGroup(RED, RADICIES)}
        self.entities = []
        self.sides = []
        self.masks = {BLUE: None, GREEN: None}
        self.contours = {}
        self.image = None
        self.current_frame = None
        self.tracked_entities={};

    def _create_mask(self, image, color):
        ''' creates a mask over a image for a color '''

        ''' resize the frame, blur it, and convert it to the
            HSV color space'''
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        ''' construct a mask for the color, then perform a series
            of dilations and erosions to remove any small blobs
            left in the mask '''
        mask = cv2.inRange(hsv, color['lower'], color['upper'])
        if (color == RED):
            mask = mask | cv2.inRange(hsv, Scalar(170, 70, 50), Scalar(180, 255, 255));

        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=3)
        return mask

    def _get_contours_by_mask(self, image, mask):
        ''' Returns balls of a given color determined by mask '''
        return cv2.findContours(mask.copy(),
                cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    def update(self, image, frame_number):
        '''
        Tracks and finds balls.
        Updates their locations.
        Doesn't check collisions.
        Assumes that the corners of image are the corners of the board.
        '''

        self.image = image
        self.current_frame = frame_number
        self.contours = {}

        '''
        For each color:
        1) Construct HSV mask
        '''
        for color in COLORS:
            mask = self._create_mask(image, HSV[color])
            self.masks[color] = mask

        '''
        2) Get contours based on mask
        3) Update entity locations (TOOD: all entities, just balls for now)
        '''
        for color in COLORS:
            contours = self._get_contours_by_mask(image, self.masks[color])
            self.contours[color] = contours
            for c in contours:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                size = self.ball_groups[color].guess_ball_size(int(x), int(y), radius)
                self.ball_groups[color].update_location(size, x, y, radius, frame_number);

        for color in COLORS:
            for ball in self.ball_groups[color].balls:
                # TODO: figure out a frame reset period
                if (ball.current_state.frame_number):
                    if (frame_number - ball.current_state.frame_number) > 3:
                        ball.reset()

        '''
        After updating each entity:
        4) update collisions of each ball
        '''

        # Yes, this is a 4-deep for-loop. This will be only num_colors * num_sizes ^2 checks though, which should only be 12 ^2
        # TODO: we can double performance easily by dynamically programming, and not checking across the diagonal
        # TODO: we can optimize this a lot in smart ways also, by keeping a notion of balls on the board, and only iterating over those.
        # TODO: we can optimize this a TON by implementing a line sweep algorithm to compute this in only nlogn time
            # -> line sweep assuming rectangles, then check for the radius intersection if its in it.
            # this would actaully have 9 * log(n) worse complexity, as we only check the balls against the augmented sweep tree.
        for color in COLORS:
            for ball in self.ball_groups[color].balls:

                ''' don't check a ball not updated this frame
                (it won't colide with anything, but something might colide with it--- that's OK) '''
                if not ball.current_state.frame_number == frame_number:
                    continue

                ''' compare to every ball for intersection '''
                for color2 in COLORS:
                    for ball2 in self.ball_groups[color2].balls:
                        # Don't have it check collision with itself (& yay for GUID's)!
                        if ball.id == ball2.id:
                            continue

                        # TODO: ensure this happens by reference, otherwise state is not updated
                        collided = ball.check_and_set_collision_with_ball(ball2)
                        if (collided == True):
                            print("COLLISON: ", color, ball.size, "with", color2, ball2.size)

    def display(self, show_mask=False, show_image=True):
        combined_mask = None
        if (show_mask):
            combined_mask = np.zeros((DISPLAY_SIZE[0], DISPLAY_SIZE[1], 3), np.uint8)

            # combine masks, convert to appropraite color
            for color in COLORS:
                # do not be fooled, it is for magical reasons going to really be in BGR
                bgr_mask = cv2.cvtColor(self.masks[color], cv2.COLOR_GRAY2RGB)
                bgr_mask[np.where((bgr_mask == [255,255,255]).all(axis = 2))] = BGR[color]
                combined_mask = combined_mask + bgr_mask

        img = None
        if (show_image):
            img = self.image

            # draw contours
            for color in COLORS:
                for ball in self.ball_groups[color].balls:
                    if ball.current_state.frame_number != self.current_frame:
                        continue
                    r = int(ball.radius)
                    c_np = ball.get_location();
                    c = (int(c_np[0]), int(c_np[1]))
                    size = ball.size;
                    cv2.circle(img, c, r, BGR[color], 2)
                    cv2.circle(img, c, 5, (255, 0, 255), -1)
                    cv2.putText(img, color + ' ' + str(size), (c[0] + 5 + r, c[1] + 5 + r), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return combined_mask, img
