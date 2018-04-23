from abc import ABC, abstractmethod
import numpy as np
from constants import *

class Event(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def as_osc_message(self):
        ...

class BallCollision(Event):
    def __init__(self, ball):
        self.ball = ball

    def as_osc_message(self):
        address = 'collide'
        message = [self.ball.size, COLLISION, self.x, self.y, self.dx, self.dy]
        return address, message

class BallMove(Event):
    def __init__(self, ball):
        self.ball = ball
        cur, prev = ball.current_state, ball.previous_state
        (self.x, self.y) = cur.get_location()
        (self.dx, self.dy) = cur.get_velocity()
        self.nframes = cur.frame_number - prev.frame_number
        self.channel = COLOR_CHANNELS[ball.color]

    def as_osc_message(self):
        address = str(self.channel)
        message = [self.ball.size, PITCHBEND, self.x, self.y, self.dx, self.dy]
        return address, message
