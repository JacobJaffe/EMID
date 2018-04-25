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
        self.channel = COLOR_CHANNELS[ball.color]

    def as_osc_message(self):
        address = '/' + str(self.channel)
        message = [self.ball.size, COLLISION, self.ball.current_state.x, self.ball.current_state.y, self.ball.current_state.dx, self.ball.current_state.dy]
        return address, message

class BallMove(Event):
    def __init__(self, ball):
        self.ball = ball
        self.channel = COLOR_CHANNELS[ball.color]

    def as_osc_message(self):
        address = '/' + str(self.channel)
        message = [self.ball.size, PITCHBEND, self.ball.current_state.x, self.ball.current_state.y, self.ball.current_state.dx, self.ball.current_state.dy]
        return address, message

class BallOff(Event):
    def __init__(self, ball):
        self.ball = ball
        self.channel = COLOR_CHANNELS[ball.color]

        def as_osc_message(self):
            address = '/' + str(self.channel)
            message = [self.ball.size, NOTE_OFF, self.ball.current_state.x, self.ball.current_state.y, self.ball.current_state.dx, self.ball.current_state.dy]
            return address, message

class BallOn(Event):
    def __init__(self, ball):
        self.ball = ball
        self.channel = COLOR_CHANNELS[ball.color]

        def as_osc_message(self):
            address = '/' + str(self.channel)
            message = [self.ball.size, NOTE_ON, self.ball.current_state.x, self.ball.current_state.y, self.ball.current_state.dx, self.ball.current_state.dy]
            return address, message
