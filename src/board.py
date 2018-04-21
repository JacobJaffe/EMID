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
        self.ball_groups = {
            BLUE: BallGroup(BLUE, RADICIES),
            GREEN: BallGroup(GREEN, RADICIES),
            RED: BallGroup(RED, RADICIES)}
        self.masks = {
            BLUE: Mask(BLUE),
            GREEN: Mask(GREEN),
            RED: Mask(RED)
        }
        self.entities = []
        self.sides = []
        self.masks = {BLUE: None, GREEN: None}
        self.contours = {}
        self.image = None
        self.current_frame = None
        self.tracked_entities={}

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
        # for mask in self.masks.values():
        #     mask.update(image)
        # for color in COLORS:
        #     mask = self._create_mask(image, HSV[color])
        #     self.masks[color] = mask

        '''
        2) Get contours based on mask
        3) Update entity locations (TOOD: all entities, just balls for now)
        '''
        for color in COLORS:
            # contours = self._get_contours_by_mask(image, self.masks[color])
            self.masks[color].update(image)
            # contours = self.masks[contours]
            contours = self.masks[color].get_contours()
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


class BallGroup():
    '''
    BallGroup:
        List of Balls, with operations to attempt ball guesing based on radius and location
        Knows the actual radicies of the balls
    '''
    def __init__(self, color, radicies):
        self.balls = [Ball(color, radicies[0], BALL_SMALL), Ball(color, radicies[1], BALL_MEDIUM), Ball(color, radicies[2], BALL_LARGE)]
        self.radicies = radicies.copy()

    def update_location(self, size, x, y, radius, frame_number):
        ''' updates location of a single ball '''
        self.balls[size].update_state(x, y, frame_number)
        self.balls[size].radius = radius

    def update_collision(self, size, in_collision):
        ''' updates the collision of a single ball '''
        self.balls[size].current_state.in_collision = in_collision

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
        print("ERROR: COULD NOT GUESS BALL SIZE")
        return -1;
