from entity import Entity
import numpy as np

COLLIDE_SPACER = 0

class Ball(Entity):
    def __init__(self, radius, color):
        Entity.__init__(self, color, frame_number=None)

        # NOTE: This will be 1, 2, or 3 based on radius of ball,
        # this will not be the actual radius of the ball
        self.radius = radius

    def on_collide(self):
        print('ball on collide {0}'.format(self.id))

    def distance_from_ball(self, ball):
        return np.linalg.norm(self.get_location() - ball.get_location())

    def check_and_set_collision_with_ball(self, ball):
        dist = self.distance_from_ball(ball)
        if self.radius + ball.radius <= dist - COLLIDE_SPACER:
            self.current_state.in_collision = True
            return True
        else:
            self.current_state.in_collision = False
            return False
