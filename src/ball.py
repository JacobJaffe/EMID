from entity import Entity
import numpy as np

COLLIDE_SPACER = 0

BALL_LARGE = 2
BALL_MEDIUM = 1
BALL_SMALL = 0

class Ball(Entity):
    def __init__(self, color, radius, size):
        Entity.__init__(self, color, frame_number=None)

        # NOTE: This will be a number 0, 1, 2 based on ball size
        self.size = size

        # this will be the actual radius detected
        self.radius = radius

    def on_collide(self):
        print('ball on collide {0}'.format(self.id))

    def _distance_from_ball(self, ball):
        return np.linalg.norm(self.get_location() - ball.get_location())

    def check_and_set_collision_with_ball(self, ball):
        dist = self._distance_from_ball(ball)
        if self.radius + ball.radius <= dist - COLLIDE_SPACER:
            self.current_state.in_collision = True
            return True
        else:
            self.current_state.in_collision = False
            return False

    def is_colliding_with_ball(self, ball):
        if self.radius + ball.radius <= dist - COLLIDE_SPACER:
            return True

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
        distances = [3649, 3649, 3649]
        for i in range(3):
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
