from abc import ABC, abstractmethod
import numpy as np
from constants import *

class Event(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def as_osc_message(self):
        ...

class BallBallCollision(Event):
    def __init__(self, ball1, ball2):
        self.ball1 = ball1
        self.ball2 = ball2

    def as_osc_message(self):
        address = 'collide'
        return address, [None]*6

class BallMove(Event):
    def __init__(self, ball):
        self.ball = ball
        cur, prev = ball.current_state, ball.previous_state
        (self.x, self.y) = cur.get_location()
        (self.dx, self.dy) = cur.get_velocity()
        self.nframes = cur.frame_number - prev.frame_number
        self.channel = COLOR_CHANNELS[ball.color]

    def as_osc_message(self):
        message = [self.ball.size, PITCHBEND, self.x, self.y, self.dx, self.dy]
        return str(self.channel), message
