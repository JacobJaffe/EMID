import numpy as np
import uuid
import abc


'''
EntityState:
    defines the location and velocity of an entity at a single frame
'''


class EntityState:
    def __init__(self):
        self.x = None
        self.y = None
        self.dx = None
        self.dy = None
        self.frame_number = None
        self.in_collision = False

    def update(self, x, y, frame_number):
        self.dx = np.abs(x-self.x)
        self.dy = np.abs(y-self.y)
        self.x = x
        self.y = y
        self.frame_number = frame_number
        self.in_collision = False

    def copy(self):
        copy_state = EntityState()
        copy_state.x = self.x
        copy_state.y = self.y
        copy_state.dx = self.dx
        copy_state.dy = self.dy
        copy_state.frame_number = self.frame_number
        return copy_state

    def get_location(self):
        return np.array([self.x, self.y])


class Entity(abc.ABC):

    def __init__(self, color, frame_number):
        self.current_state = EntityState(frame_number)
        self.color = color
        self.id = uuid.uuid1()
        self.previous_state = None

    def update_state(self, x, y, frame_number):
        self.previous_state = self.current_state.copy()
        self.current_state.update(x, y, frame_number)

    def get_location(self):
        return self.current_state.get_location()

    def is_in_new_collision(self):
        return self.current_state.in_collision\
                and not self.previous_state.in_collision

    @abc.abstract_method
    def on_collide(self):
        ...

    @abc.abstract_method
    def is_colliding_with_ball(self, ball):
        ...
