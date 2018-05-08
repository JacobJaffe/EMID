from entity import Entity
from constants import *

class Side(Entity):
    def __init__(self, name):
        Entity.__init__(self, None, None)
        self.name = name
        self.height = None
        self.width = None
        self.spacer = COLLIDE_SPACER

    def update(self, height, width):
        self.height = height
        self.width = width

    def is_colliding_with_ball(self, ball):
        if not ball.exists():
            return False
        x, y = ball.get_location()
        r = ball.radius
        if self.name == 'top':
            return y + r > self.height - self.spacer
        elif self.name == 'left':
            return x - r < self.spacer
        elif self.name == 'right':
            return x + r > self.spacer
