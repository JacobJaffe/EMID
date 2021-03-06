''' Colors and shit '''
BLUE, GREEN, YELLOW, RED, ORANGE, MAROON = 'blue', 'green', 'yellow', 'red', 'orange', 'maroon'
COLORS = [BLUE, GREEN, RED, YELLOW, ORANGE, MAROON]

BLUE_BGR = (255, 0, 0)
GREEN_BGR = (0, 255, 0)
YELLOW_BGR = (0, 255, 255)
RED_BGR = (0, 0, 255)
ORANGE_BGR = (0, 165, 255)
MAROON_BGR = (0, 22, 100)

BGR = {BLUE: BLUE_BGR,
        GREEN: GREEN_BGR,
        RED: RED_BGR,
        YELLOW: YELLOW_BGR,
        ORANGE: ORANGE_BGR,
        MAROON: MAROON_BGR}


# TODO: pallets: Blue, Yellow, Red

''' MIDI API Shit, for MAX'''
COLOR_CHANNELS = {BLUE: 1, GREEN: 2, RED: 3, YELLOW: 4, ORANGE: 5, MAROON: 6}
NOTE_ON, NOTE_OFF, PITCH_BEND, COLLISION = 1, 2, 3, 4
BALL_LARGE = 2
BALL_MEDIUM = 1
BALL_SMALL = 0

''' Misc '''
# RADICIES = [20.] # TODO: make multiple work!
RADICIES = [20.] # TODO: make multiple work!

COLLIDE_THRESH = 1.1
COLLIDE_SPACER = 7.5
DISPLAY_SIZE = [600, 600]
EXPOSURE = 2000
XMAX = 500.0
YMAX = 500.0
