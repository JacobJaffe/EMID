from ball import Ball
from mask import Mask
from entity import Entity
import cv2
import numpy as np
from constants import *
from events import *


class Board:
    '''
    Board:
        keeps track of balls on the board and is responsible for
        detecting collisions and sending events to the dispatcher
    '''
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.masks = {c: Mask(c) for c in COLORS}
        self.entities = []
        self.sides = []
        # self.masks = {BLUE: None, GREEN: None}
        self.contours = {}
        self.image = None
        self.current_frame = None
        self.tracked_entities={}
        self.width = None
        self.height = None

    def update(self, image, frame_number):

        '''
        Tracks and finds balls.
        Updates their locations.
        Checks collisions.
        Assumes that the corners of image are the corners of the board.
        '''

        self.width, self.height = image.shape[:2]

        self.image = image
        self.current_frame = frame_number
        self.contours = {}
        '''
        For each color:
        1) Construct HSV mask
        2) Get contours based on mask
        3) Update entity locations (TOOD: all entities, just balls for now)
        '''
        for color in COLORS:
            self.masks[color].update(image, frame_number)
            contours = self.masks[color].get_contours()

            # TODO: This can now be accessed through masks
            self.contours[color] = contours

        '''
        After updating each entity:
        4) update collisions of each ball
        '''
        for color in COLORS:
            for ball in self.masks[color].balls:

                ''' don't check a ball not updated this frame
                (it won't colide with anything, but something might colide with it--- that's OK) '''
                # if not ball.current_state.frame_number == frame_number:
                #     continue
                ''' compare to every side for intersection '''
                # TODO: have this be different for each side?
                isColidingWithSides = ball.check_colliding_sides(self.width, self.height)
                if isColidingWithSides:
                    print("SIDE COLLISION: ", color, ball.size)


                ''' compare to every ball for intersection '''
                for color2 in COLORS:
                    for ball2 in self.masks[color2].balls:
                        # Don't have it check collision with itself (& yay for GUID's)!
                        if ball.id == ball2.id:
                            continue

                        isColidingWithBall = ball.check_coliding_ball(ball2)
                        if isColidingWithBall:
                            print("COLLISON: ", color, ball.size, "with", color2, ball2.size)
        return

    def send_events(self):
        ''' reset entities send note offs (previously done in mask) '''
        for m in self.masks.values():
            for ball in m.balls:
                if not ball.current_state.frame_number:
                    continue
                if self.current_frame - ball.current_state.frame_number > 3:
                    ball.reset()
                    if not ball.current_state or not ball.current_state.x:
                        event = BallOff(ball)
                        if ball.previous_state and ball.previous_state.x:
                            print("(REAL?) NOTE OFF: ", ball.color, ball.size)
                        self.dispatcher.send(event)

        ''' send ball move, note on and collisions '''
        for color in COLORS:
            for ball in self.masks[color].balls:
                ball.send_events(self.dispatcher)

    def display(self, show_mask=False, show_image=True):
        combined_mask = None
        if (show_mask):
            # combine masks, convert to appropraite color
            # do not be fooled, it is for magical reasons going to really be in BGR
            combined_mask = np.sum(m.get_bgr() for m in self.masks.values())

        img = None
        if (show_image):
            img = self.image

            # draw contours
            for color in COLORS:
                for ball in self.masks[color].balls:
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
