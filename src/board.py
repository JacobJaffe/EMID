from ball import Ball
from mask import Mask
from entity import Entity
import cv2
import numpy as np
from constants import *


class Board:
    '''
    Board:
        keeps track of balls on the board and is responsible for
        detecting collisions and sending events to the dispatcher
    '''
    def __init__(self):
        self.masks = {c: Mask(c) for c in COLORS}
        self.entities = []
        self.sides = []
        # self.masks = {BLUE: None, GREEN: None}
        self.contours = {}
        self.image = None
        self.current_frame = None
        self.tracked_entities={}

    def update(self, image, frame_number, dispatcher):
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
        2) Get contours based on mask
        3) Update entity locations (TOOD: all entities, just balls for now)
        '''
        for color in COLORS:
            self.masks[color].update(image, frame_number, dispatcher)
            contours = self.masks[color].get_contours()

            # TODO: This can now be accessed through masks
            self.contours[color] = contours

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
            for ball in self.masks[color].balls:

                ''' don't check a ball not updated this frame
                (it won't colide with anything, but something might colide with it--- that's OK) '''
                # if not ball.current_state.frame_number == frame_number:
                #     continue

                ''' compare to every ball for intersection '''
                for color2 in COLORS:
                    for ball2 in self.masks[color2].balls:
                        # Don't have it check collision with itself (& yay for GUID's)!
                        if ball.id == ball2.id:
                            continue

                        # TODO: ensure this happens by reference, otherwise state is not updated
                        collided = ball.check_and_set_collision_with_ball(ball2)
                        if (collided == True):
                            print("COLLISON: ", color, ball.size, "with", color2, ball2.size)
        return

    def send_events(self, dispatcher):
        for color in COLORS:
            for ball in self.masks[color].balls:
                ball.send_events(dispatcher)

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
