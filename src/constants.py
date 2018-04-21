BLUE, GREEN, YELLOW, RED = 'blue', 'green', 'yellow', 'red'
COLORS = [BLUE, GREEN, RED] # TODO: , YELLOW, RED]
RADICIES = [7., 14., 20.]

DISPLAY_SIZE = [600, 600]

GREEN_HSV = {'lower': (65,60,60), 'upper': (80,255,255)}
BLUE_HSV = {'lower': (102, 93, 72), 'upper': (119, 255, 255)}
RED_HSV = {'lower': (0, 70, 50), 'upper': (10, 255, 255)}
YELLOW_HSV = {'lower': (0, 0, 0), 'upper': (0, 0, 0)}

BLUE_BGR = (255, 0, 0)
GREEN_BGR = (0, 255, 0)
YELLOW_BGR = (0, 255, 255)
RED_BGR = (0, 0, 255)

BGR = {BLUE: BLUE_BGR,
        GREEN: GREEN_BGR,
        RED: RED_BGR,
        YELLOW: YELLOW_BGR}

HSV = {BLUE: BLUE_HSV,
        GREEN: GREEN_HSV,
        RED: RED_HSV,
        YELLOW: YELLOW_HSV}
        
COLOR_CHANNELS = {BLUE: 1, GREEN: 2, RED: 3}
NOTEON, NOTEOFF, PITCHBEND, COLLISION = 1, 2, 3, 4
