from ball import Ball
from mask import Mask
from entity import Entity
from side import Side
import cv2
import numpy as np
from events import *
from constants import *


class Board:
    '''
    Board:
        keeps track of balls on the board and is responsible for
        detecting collisions and sending events to the dispatcher
    '''
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.masks = {c: Mask(c, dispatcher) for c in COLORS}
        self.entities = []
        self.sides = [Side(name) for name in ['top','left','right']]
        self.image = None
        self.current_frame = None
        self.tracked_entities={}
        self.width = None
        self.height = None
        self.collisions = None
        self.balls = None

    def get_balls(self):
        return [b for m in self.masks.values() for b in m.balls]

    def set_collisions(self):
        ''' set_collisions(self):
                updates internal self.collisions matrix
                rows are balls and columns are entities = balls + sides + shapes
        '''
        # Balls and Sides are immutable, polygons will appear
        # and disappear. Need to account for this.
        balls = self.get_balls()
        ball_ids = [b.id for b in balls]
        entities = balls + self.sides
        if self.collisions is None:
            self.collisions = {}
            for b in balls:
                self.collisions[b.id] = {}
        for b in balls:
            for e in entities:
                # if entity not previously found, set to 0
                if e.id not in self.collisions[b.id]:
                    self.collisions[b.id][e.id] = 0
                v = self.collisions[b.id][e.id]
                if e.is_colliding_with_ball(b):
                    if v == 0:
                        v = 1
                    elif v == 1:
                        v = 2
                else:
                    v = 0
                self.collisions[b.id][e.id] = v

    def send_collisions(self):
        balls = self.get_balls()
        entities = balls + self.sides
        for b in balls:
            for e in entities:
                v = self.collisions[b.id][e.id]
                if v == 1:
                    try:
                        print("COLLISON: ", b.color, b.size, "with", e.color, e.size)
                    except:
                        continue
                    self.dispatcher.send(BallCollision(b,e))

    def update(self, image, frame_number):
        '''
        Tracks and finds balls.
        Updates their locations.
        Checks collisions.
        Assumes that the corners of image are the corners of the board.
        '''
        self.image = image
        self.current_frame = frame_number

        ''' Get height and width from image and update sides '''
        self.width, self.height = self.image.shape[:2]
        [s.update(self.height, self.width) for s in self.sides]

        '''
        For each color:
        1) Construct HSV mask
        2) Get contours based on mask
        3) Update entity locations (TOOD: all entities, just balls for now)
        '''

        # Update masks
        [mask.update(image, frame_number) for mask in self.masks.values()]

        '''
        After updating each entity:
        4) send collision messages
        '''
        self.set_collisions()
        return

    # TODO: we should be sending messages AS SOON as we have information
    # This function will likely be completely eliminated
    def send_events(self):
        ''' reset entities send note offs (previously done in mask) '''
        '''
        for m in self.masks.values():
            for ball in m.balls:
                if not ball.current_state.frame_number:
                    continue
                if self.current_frame - ball.current_state.frame_number > 3:
                    ball.reset()
                    if (not ball.current_state) or (not ball.current_state.x):
                        event = BallOff(ball)
                        if ball.previous_state and ball.previous_state.x:
                            print("(REAL?) NOTE OFF: ", ball.color, ball.size)
                        self.dispatcher.send(event)
                        '''

        for msg in self.dispatcher.get_messages():
            print("Recieved message: ", msg)
            if msg == 1:
                map(self.reset_color, [BLUE, GREEN])
            elif msg == 2:
                map(self.reset_color, [RED, YELLOW, ORANGE])
            elif msg == 3:
                map(self.reset_color, [])

        ''' send ball move, note on and collisions '''
        for color in COLORS:
            for ball in self.masks[color].balls:
                ball.send_events(self.dispatcher)
        self.send_collisions()

    def reset_color(self, color):
        for ball in self.masks[color].balls:
            if ball.previous_state is not None:
                ball.previous_state.reset()

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
                    # cv2.putText(img, color + ' ' + str(size), (c[0] + 5 + r, c[1] + 5 + r), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return combined_mask, img
