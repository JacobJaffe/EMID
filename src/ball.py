from entity import Entity
import numpy as np
from constants import *
from events import *

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

    def _distance_from_point(self, point):

        point = np.array(point)
        return np.linalg.norm(self.get_location() - point)

    def check_and_set_collision_with_ball(self, ball):
        # gotta exist
        if (not self.current_state.x) or (not self.current_state.y) or (not ball.current_state.x) or (not ball.current_state.y):
            self.current_state.in_collision = False
            return False
        # gotta be around for a little
        # if (not self.previous_state.x) or (not self.previous_state.y) or (not ball.previous_state.x) or (not ball.previous_state.y):
        #     return False


        dist = self._distance_from_ball(ball)
        # # Make sure self-collision errors don't happen
        # if dist < self.radius/4:
        #     return False
        if (self.radius + ball.radius) >= (dist - COLLIDE_SPACER):
            self.current_state.in_collision = True
            return True
            
        self.current_state.in_collision = False
        return False

    def is_colliding_with_ball(self, ball):
        if self.radius + ball.radius <= dist - COLLIDE_SPACER:
            return True

    def send_events(self, dispatcher):
        '''
        Sends pitch bend events, Note on events, note off events, and collision events
        '''

        if (self.previous_state and self.previous_state.x):
            if (self.current_state and self.current_state.x):
                event = BallMove(self)
                print("BALL MOVE: ", self.color, self.size)
                dispatcher.send(event)

        '''
        TODO: send on, off, bend pitch
        '''
        if (not self.previous_state or not self.previous_state.x):
            if (self.current_state and self.current_state.x):
                event = BallOn(self)
                print("NOTE ON: ", self.color, self.size)
                dispatcher.send(event)

        '''
        Send collisions:
        '''
        if (self.current_state.in_collision):
            event = BallCollision(self)
            dispatcher.send(event)
